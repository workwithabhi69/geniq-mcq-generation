"""
GENIQ - Pydantic Schemas for MCQ Generation, Evaluation and Research
====================================================================
Ensures strict validation of structured model outputs and API payloads.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class DifficultyEnum(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class PromptStrategyEnum(str, Enum):
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    STRUCTURED = "structured"

class ModelVariantEnum(str, Enum):
    PRIMARY = "primary"
    LITE = "lite"

class MCQOptions(BaseModel):
    A: str = Field(..., description="Option A")
    B: str = Field(..., description="Option B")
    C: str = Field(..., description="Option C")
    D: str = Field(..., description="Option D")

    @field_validator("A", "B", "C", "D")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Option text cannot be empty.")
        return v_clean

class MCQOutput(BaseModel):
    """
    Standardized MCQ output schema required across all models and prompting strategies.
    """
    question: str = Field(..., description="The multiple choice question text")
    options: MCQOptions = Field(..., description="Exactly four options: A, B, C, D")
    correct_answer: str = Field(..., description="The key of the correct option ('A', 'B', 'C', or 'D')")
    explanation: str = Field(..., description="Explanation based explicitly on the source passage")
    difficulty: str = Field(default="Medium", description="Difficulty level: Easy, Medium, or Hard")
    source_evidence: str = Field(..., description="Exact or verbatim supporting excerpt from the passage")
    topic: str = Field(default="Science", description="Subject or topic of the question")
    generation_model: str = Field(..., description="Identifier of the model used")
    prompt_strategy: str = Field(..., description="Strategy used: zero_shot, few_shot, or structured")

    @field_validator("correct_answer")
    @classmethod
    def validate_correct_key(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in ["A", "B", "C", "D"]:
            raise ValueError(f"Correct answer must be one of ['A', 'B', 'C', 'D'], received: {v}")
        return v_upper

    @field_validator("options")
    @classmethod
    def validate_unique_options(cls, v: MCQOptions) -> MCQOptions:
        opts = [v.A.lower().strip(), v.B.lower().strip(), v.C.lower().strip(), v.D.lower().strip()]
        if len(set(opts)) < 4:
            raise ValueError(f"Duplicate options detected in generated MCQ: {opts}")
        return v

class GenerationRequest(BaseModel):
    passage: Optional[str] = Field(None, description="Source educational passage")
    topic: Optional[str] = Field(None, description="Topic or prompt context if no raw passage provided")
    num_questions: int = Field(default=1, ge=1, le=10, description="Number of questions to generate")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.MEDIUM)
    prompt_strategy: PromptStrategyEnum = Field(default=PromptStrategyEnum.STRUCTURED)
    model_name: Optional[str] = Field(None, description="Override model ID if specified")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)

class GenerationResponse(BaseModel):
    success: bool
    questions: List[MCQOutput]
    total_generated: int
    latency_ms: float
    model_used: str
    prompt_strategy: str
    error: Optional[str] = None

class HumanEvaluationRating(BaseModel):
    question_id: Optional[str] = None
    relevance_score: int = Field(..., ge=1, le=5, description="1=Very poor to 5=Excellent")
    correctness_score: int = Field(..., ge=1, le=5)
    clarity_score: int = Field(..., ge=1, le=5)
    distractor_plausibility_score: int = Field(..., ge=1, le=5)
    uniqueness_score: int = Field(..., ge=1, le=5)
    difficulty_score: int = Field(..., ge=1, le=5)
    reviewer_id: str = Field(default="reviewer_1")
    comments: Optional[str] = None

class AutomatedEvaluationResult(BaseModel):
    benchmark_id: str
    semantic_similarity: float = Field(..., description="Cosine similarity with reference question via embeddings")
    reference_answer_matched: bool = Field(..., description="Whether generated answer matches reference key/concept")
    schema_valid: bool = Field(..., description="Whether schema passed Pydantic validation")
    unique_options: bool = Field(..., description="True if no duplicate distractors")
    grounding_score: float = Field(..., description="Lexical/semantic grounding in passage")
    latency_ms: float = Field(..., description="Generation latency in milliseconds")
    generation_success: bool = Field(...)
    generated_mcq: Optional[MCQOutput] = None
    error: Optional[str] = None
