"""
GENIQ - Research Experiment Pipeline
====================================
Runs controlled experiments comparing:
- Experiment A: Primary Model + Zero-Shot
- Experiment B: Primary Model + Few-Shot
- Experiment C: Primary Model + Structured
- Experiment D: Lite Model + Structured

Exports results to CSV/JSON, calculates comparative metrics,
and detects failure cases.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from app.generation.gemini_generator import GeminiGenerator
from app.evaluation.metrics import EvaluationEngine

logger = logging.getLogger(__name__)

EXPERIMENTS_CONFIG = {
    "exp_a": {
        "id": "exp_a",
        "name": "Experiment A (Primary + Zero-Shot)",
        "model_key": "PRIMARY_MODEL",
        "default_model": "gemini-flash-lite-latest",
        "strategy": "zero_shot",
        "description": "Primary Gemini model with zero-shot prompting on SciQ benchmark."
    },
    "exp_b": {
        "id": "exp_b",
        "name": "Experiment B (Primary + Few-Shot)",
        "model_key": "PRIMARY_MODEL",
        "default_model": "gemini-flash-lite-latest",
        "strategy": "few_shot",
        "description": "Primary Gemini model with domain few-shot exemplars."
    },
    "exp_c": {
        "id": "exp_c",
        "name": "Experiment C (Primary + Structured)",
        "model_key": "PRIMARY_MODEL",
        "default_model": "gemini-flash-lite-latest",
        "strategy": "structured",
        "description": "Primary Gemini model with explicit psychometric structured prompting."
    },
    "exp_d": {
        "id": "exp_d",
        "name": "Experiment D (Lite + Structured)",
        "model_key": "LITE_MODEL",
        "default_model": "gemini-flash-lite-latest",
        "strategy": "structured",
        "description": "Lightweight Gemini model with the same structured prompting for cross-model comparison."
    }
}

class ResearchRunner:
    """Orchestrates controlled research experiments across models and strategies."""

    def __init__(self, benchmark_file: str, output_dir: str = "research/results"):
        self.benchmark_file = benchmark_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.generator = GeminiGenerator()
        self.evaluator = EvaluationEngine()

    def load_benchmark(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads SciQ benchmark records."""
        if not os.path.exists(self.benchmark_file):
            raise FileNotFoundError(f"Benchmark file not found at {self.benchmark_file}")
        
        if self.benchmark_file.endswith(".csv"):
            df = pd.read_csv(self.benchmark_file)
        else:
            df = pd.read_json(self.benchmark_file, lines=True)

        records = df.to_dict(orient="records")
        if limit:
            records = records[:limit]
        return records

    def run_experiment(self, exp_key: str, sample_limit: Optional[int] = 10) -> Dict[str, Any]:
        """Runs a designated experiment on the benchmark sample."""
        if exp_key not in EXPERIMENTS_CONFIG:
            raise ValueError(f"Unknown experiment '{exp_key}'. Choices: {list(EXPERIMENTS_CONFIG.keys())}")

        cfg = EXPERIMENTS_CONFIG[exp_key]
        model_name = os.getenv(cfg["model_key"], cfg["default_model"])
        strategy = cfg["strategy"]

        records = self.load_benchmark(limit=sample_limit)
        logger.info(f"Running {cfg['name']} on {len(records)} benchmark items using {model_name}...")

        results_list = []
        detailed_items = []
        failure_cases = []

        for idx, item in enumerate(records):
            passage = item.get("support", "")
            benchmark_id = item.get("benchmark_id", f"ITEM_{idx+1:04d}")

            if not self.generator.is_configured():
                # API not configured - do not fake data
                return {
                    "experiment_id": exp_key,
                    "name": cfg["name"],
                    "status": "pending_configuration",
                    "error": "Gemini API key is not configured. Please supply a valid GEMINI_API_KEY in backend/.env to execute live experiments.",
                    "total_samples": len(records),
                    "evaluated_samples": 0
                }

            mcq_output, latency_ms, error = self.generator.generate_single_mcq(
                passage=passage,
                strategy=strategy,
                model_name=model_name,
                difficulty="Medium",
                topic="Science"
            )

            if mcq_output is not None:
                eval_metrics = self.evaluator.evaluate_generated_mcq(
                    generated_mcq_dict=mcq_output.dict(),
                    reference_record=item,
                    latency_ms=latency_ms
                )
                eval_metrics["benchmark_id"] = benchmark_id
                eval_metrics["generated_question"] = mcq_output.question
                eval_metrics["generated_answer"] = mcq_output.options.dict()[mcq_output.correct_answer]
                eval_metrics["reference_question"] = item.get("question", "")
                eval_metrics["reference_answer"] = item.get("correct_answer", "")
                results_list.append(eval_metrics)
                detailed_items.append(mcq_output.dict())

                if not eval_metrics.get("answer_matched") or eval_metrics.get("grounding_score", 0) < 0.5:
                    failure_cases.append({
                        "benchmark_id": benchmark_id,
                        "generated": mcq_output.dict(),
                        "reference_question": item.get("question"),
                        "reference_answer": item.get("correct_answer"),
                        "grounding_score": eval_metrics.get("grounding_score")
                    })
            else:
                results_list.append({
                    "benchmark_id": benchmark_id,
                    "schema_valid": False,
                    "unique_options": False,
                    "semantic_similarity": 0.0,
                    "answer_matched": False,
                    "grounding_score": 0.0,
                    "latency_ms": latency_ms,
                    "success": False,
                    "errors": [error or "Unknown generation error"]
                })

        # Calculate aggregated metrics
        df_res = pd.DataFrame(results_list)
        total_eval = len(df_res)
        valid_schema_rate = float(df_res["schema_valid"].mean() * 100) if total_eval > 0 else 0.0
        answer_match_rate = float(df_res["answer_matched"].mean() * 100) if total_eval > 0 else 0.0
        avg_grounding = float(df_res["grounding_score"].mean()) if total_eval > 0 else 0.0
        avg_semantic_sim = float(df_res["semantic_similarity"].mean()) if total_eval > 0 else 0.0
        avg_latency = float(df_res["latency_ms"].mean()) if total_eval > 0 else 0.0

        summary = {
            "experiment_id": exp_key,
            "name": cfg["name"],
            "model": model_name,
            "strategy": strategy,
            "status": "completed",
            "total_samples": total_eval,
            "valid_schema_rate": round(valid_schema_rate, 2),
            "answer_correctness_rate": round(answer_match_rate, 2),
            "average_grounding_score": round(avg_grounding, 3),
            "average_semantic_similarity": round(avg_semantic_sim, 3),
            "average_latency_ms": round(avg_latency, 1),
            "failure_case_count": len(failure_cases)
        }

        # Save results
        res_file = os.path.join(self.output_dir, f"{exp_key}_results.json")
        with open(res_file, "w", encoding="utf-8") as f:
            json.dump({
                "summary": summary,
                "items": results_list,
                "failure_cases": failure_cases[:10]
            }, f, indent=2)

        return summary
