"""
GENIQ - SciQ Dataset Acquisition and Preprocessing Pipeline
===========================================================
This module handles downloading, inspecting, cleaning, filtering, and preparing
the SciQ dataset (Welbl et al., 2017) under CC BY-NC 3.0 license.

Protocol:
- Inspect schema, missing values, duplicates, and token/character length distributions.
- Filter out records with missing/empty 'support' passages.
- Preserve original train, validation, and test splits.
- Extract a reproducible sample of 200 items from the test split with a fixed random seed.
- Generate statistics summary and persist processed subsets in CSV and JSONL formats.
"""

import os
import json
import logging
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RANDOM_SEED = 42
DEFAULT_EVAL_SAMPLE_SIZE = 200

def clean_text(text: Optional[str]) -> str:
    """Clean whitespace, control characters, and leading/trailing spaces."""
    if not text or not isinstance(text, str):
        return ""
    # Normalize whitespaces
    cleaned = " ".join(text.strip().split())
    return cleaned

def process_sciq_dataset(
    output_dir: str = "research/data",
    eval_sample_size: int = DEFAULT_EVAL_SAMPLE_SIZE,
    seed: int = RANDOM_SEED
) -> Dict[str, Any]:
    """
    Downloads, inspects, filters, and saves SciQ dataset splits.
    Returns statistical summary of the dataset.
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info("Loading SciQ dataset from Hugging Face...")
    
    try:
        from datasets import load_dataset
        dataset = load_dataset("allenai/sciq")
    except Exception as e:
        logger.error(f"Failed to load dataset via datasets library: {e}")
        raise e

    stats: Dict[str, Any] = {
        "dataset_name": "allenai/sciq",
        "license": "CC BY-NC 3.0",
        "citation": "Welbl, Liu and Gardner (2017) - Crowdsourcing Multiple Choice Science Questions",
        "raw_counts": {},
        "filtered_counts": {},
        "removed_empty_support": {},
        "text_statistics": {}
    }

    processed_dfs = {}

    for split in ["train", "validation", "test"]:
        raw_split = dataset[split]
        raw_count = len(raw_split)
        stats["raw_counts"][split] = raw_count
        logger.info(f"Loaded {split} split: {raw_count} records.")

        df = pd.DataFrame(raw_split)
        
        # Clean text columns
        for col in ["question", "support", "correct_answer", "distractor1", "distractor2", "distractor3"]:
            if col in df.columns:
                df[col] = df[col].apply(clean_text)

        # Identify missing or empty support
        empty_support_mask = df["support"] == ""
        removed_count = int(empty_support_mask.sum())
        stats["removed_empty_support"][split] = removed_count

        # Filter usable records: must have support, question, correct_answer, and 3 distractors
        usable_mask = (
            (df["support"] != "") &
            (df["question"] != "") &
            (df["correct_answer"] != "") &
            (df["distractor1"] != "") &
            (df["distractor2"] != "") &
            (df["distractor3"] != "")
        )
        filtered_df = df[usable_mask].copy().reset_index(drop=True)
        stats["filtered_counts"][split] = len(filtered_df)
        logger.info(f"Filtered {split} split: {len(filtered_df)} usable records ({removed_count} removed due to missing/empty fields).")

        # Compute lengths
        filtered_df["support_char_len"] = filtered_df["support"].apply(len)
        filtered_df["question_char_len"] = filtered_df["question"].apply(len)
        filtered_df["support_word_len"] = filtered_df["support"].apply(lambda x: len(x.split()))
        filtered_df["question_word_len"] = filtered_df["question"].apply(lambda x: len(x.split()))

        # Save processed splits
        csv_path = os.path.join(output_dir, f"sciq_{split}_processed.csv")
        jsonl_path = os.path.join(output_dir, f"sciq_{split}_processed.jsonl")
        filtered_df.to_csv(csv_path, index=False)
        filtered_df.to_json(jsonl_path, orient="records", lines=True)

        processed_dfs[split] = filtered_df

        stats["text_statistics"][split] = {
            "avg_support_words": float(filtered_df["support_word_len"].mean()),
            "avg_question_words": float(filtered_df["question_word_len"].mean()),
            "min_support_words": int(filtered_df["support_word_len"].min()),
            "max_support_words": int(filtered_df["support_word_len"].max())
        }

    # Extract reproducible sample from test split for evaluation benchmark
    test_df = processed_dfs["test"]
    actual_sample_size = min(eval_sample_size, len(test_df))
    eval_benchmark_sample = test_df.sample(n=actual_sample_size, random_state=seed).copy().reset_index(drop=True)
    
    # Assign unique benchmark IDs
    eval_benchmark_sample["benchmark_id"] = [f"SCIQ_TEST_{i+1:04d}" for i in range(len(eval_benchmark_sample))]

    benchmark_csv = os.path.join(output_dir, f"sciq_test_benchmark_{actual_sample_size}.csv")
    benchmark_jsonl = os.path.join(output_dir, f"sciq_test_benchmark_{actual_sample_size}.jsonl")
    eval_benchmark_sample.to_csv(benchmark_csv, index=False)
    eval_benchmark_sample.to_json(benchmark_jsonl, orient="records", lines=True)

    stats["benchmark_sample"] = {
        "size": actual_sample_size,
        "seed": seed,
        "saved_csv": benchmark_csv,
        "saved_jsonl": benchmark_jsonl
    }

    # Save summary stats
    stats_path = os.path.join(output_dir, "sciq_preprocessing_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    logger.info(f"SciQ dataset processing completed. Summary saved to {stats_path}")
    return stats

if __name__ == "__main__":
    import sys
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(base_dir, "research", "data")
    stats = process_sciq_dataset(output_dir=out_dir)
    print(json.dumps(stats, indent=2))
