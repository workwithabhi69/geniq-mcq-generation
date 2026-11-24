"""
GENIQ - Automated & Human Evaluation Engine
===========================================
Implements formal research metrics for comparing MCQ generation:
1. Automated Metrics:
   - Semantic Similarity with reference question (Sentence Transformers / cosine similarity)
   - Normalized Answer Matching (matching reference correct answer)
   - Schema & Structure Validity Rate (Pydantic validation)
   - Distractor Uniqueness Rate (checking duplicate options)
   - Lexical & Semantic Context Grounding Score (token overlap / containment in source passage)
   - Generation Latency (milliseconds per item)
   - Cost & Token Estimation

2. Human Evaluation Metrics (Likert 1-5 scale):
   - Relevance to passage
   - Factual correctness
   - Question clarity
   - Distractor plausibility
   - Uniqueness of correct answer
   - Appropriate difficulty
   - Inter-rater agreement (Cohen's Kappa)
"""

import re
import string
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class EvaluationEngine:
    """Computes automated evaluation metrics for generated MCQs against reference data."""

    def __init__(self, embedder_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedder_model_name = embedder_model_name
        self._embedder = None

    def _get_embedder(self):
        """Lazy load sentence-transformer model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer: {self.embedder_model_name}...")
                self._embedder = SentenceTransformer(self.embedder_model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to Jaccard similarity.")
                self._embedder = None
        return self._embedder

    @staticmethod
    def normalize_text(text: str) -> str:
        """Lowercases text, strips punctuation, and normalizes whitespaces."""
        if not text:
            return ""
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        return " ".join(text.split())

    def compute_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Computes cosine similarity between two sentences using embeddings."""
        if not text_a or not text_b:
            return 0.0

        embedder = self._get_embedder()
        if embedder is not None:
            embeddings = embedder.encode([text_a, text_b], convert_to_numpy=True)
            norm_a = np.linalg.norm(embeddings[0])
            norm_b = np.linalg.norm(embeddings[1])
            if norm_a == 0 or norm_b == 0:
                return 0.0
            similarity = float(np.dot(embeddings[0], embeddings[1]) / (norm_a * norm_b))
            return max(0.0, min(1.0, similarity))

        # Fallback to Jaccard word-level similarity
        tokens_a = set(self.normalize_text(text_a).split())
        tokens_b = set(self.normalize_text(text_b).split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)
        return float(len(intersection) / len(union)) if union else 0.0

    def compute_answer_match(self, generated_answer_text: str, reference_answer_text: str) -> bool:
        """Checks if generated answer matches the reference answer (normalized exact or substring)."""
        norm_gen = self.normalize_text(generated_answer_text)
        norm_ref = self.normalize_text(reference_answer_text)
        if not norm_gen or not norm_ref:
            return False
        return (norm_gen == norm_ref) or (norm_gen in norm_ref) or (norm_ref in norm_gen)

    def compute_grounding_score(self, source_passage: str, generated_question: str, generated_answer: str, source_evidence: str) -> float:
        """
        Computes grounding score based on:
        1. Whether evidence exists verbatim or near-verbatim in source passage.
        2. Content word overlap of the question and answer with the passage.
        """
        norm_source = self.normalize_text(source_passage)
        norm_evidence = self.normalize_text(source_evidence)

        # Evidence verification component (0.0 to 0.5)
        evidence_score = 0.0
        if norm_evidence and norm_evidence in norm_source:
            evidence_score = 0.5
        elif norm_evidence:
            evidence_score = 0.5 * self.compute_semantic_similarity(source_evidence, source_passage)

        # Answer & Question token containment (0.0 to 0.5)
        qa_tokens = set(self.normalize_text(f"{generated_question} {generated_answer}").split())
        source_tokens = set(norm_source.split())
        if qa_tokens and source_tokens:
            contained = qa_tokens.intersection(source_tokens)
            lexical_score = 0.5 * (len(contained) / len(qa_tokens))
        else:
            lexical_score = 0.0

        return float(min(1.0, evidence_score + lexical_score))

    def evaluate_generated_mcq(
        self,
        generated_mcq_dict: Dict[str, Any],
        reference_record: Dict[str, Any],
        latency_ms: float
    ) -> Dict[str, Any]:
        """
        Performs comprehensive automated evaluation on a single generated MCQ
        against its reference SciQ record.
        """
        eval_result = {
            "schema_valid": False,
            "unique_options": False,
            "semantic_similarity": 0.0,
            "answer_matched": False,
            "grounding_score": 0.0,
            "latency_ms": latency_ms,
            "success": False,
            "errors": []
        }

        # Check schema
        from app.schemas.mcq import MCQOutput
        try:
            validated = MCQOutput(**generated_mcq_dict)
            eval_result["schema_valid"] = True
            eval_result["unique_options"] = True
        except Exception as e:
            eval_result["errors"].append(str(e))
            return eval_result

        # Reference fields
        ref_q = reference_record.get("question", "")
        ref_a = reference_record.get("correct_answer", "")
        passage = reference_record.get("support", "")

        # Generated fields
        gen_q = validated.question
        opts = validated.options.dict()
        correct_key = validated.correct_answer
        gen_a = opts.get(correct_key, "")
        evidence = validated.source_evidence

        # Metrics
        eval_result["semantic_similarity"] = self.compute_semantic_similarity(gen_q, ref_q)
        eval_result["answer_matched"] = self.compute_answer_match(gen_a, ref_a)
        eval_result["grounding_score"] = self.compute_grounding_score(passage, gen_q, gen_a, evidence)
        eval_result["success"] = True

        return eval_result

    @staticmethod
    def calculate_cohens_kappa(ratings_rater1: List[int], ratings_rater2: List[int]) -> float:
        """
        Computes Cohen's Kappa for inter-rater reliability on 1-5 Likert scales.
        """
        if len(ratings_rater1) != len(ratings_rater2) or len(ratings_rater1) == 0:
            return 0.0
        try:
            from sklearn.metrics import cohen_kappa_score
            return float(cohen_kappa_score(ratings_rater1, ratings_rater2))
        except Exception as e:
            logger.warning(f"Failed to calculate Cohen's Kappa: {e}")
            return 0.0
