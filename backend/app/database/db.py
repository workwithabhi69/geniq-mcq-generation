"""
GENIQ - SQLite Database Models
==============================
Provides persistent storage for:
- Generated and saved MCQs
- Execution logs and benchmark results
- Human evaluation reviews
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class QuestionModel(Base):
    """Stores generated and user-curated multiple-choice questions."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=False)
    source_evidence = Column(Text, nullable=True)
    source_passage = Column(Text, nullable=True)
    topic = Column(String(100), default="Science")
    difficulty = Column(String(50), default="Medium")
    generation_model = Column(String(100), nullable=False)
    prompt_strategy = Column(String(50), nullable=False)
    is_saved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ExperimentRecordModel(Base):
    """Stores experimental runs and metrics."""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(50), index=True)
    name = Column(String(200), nullable=False)
    model = Column(String(100), nullable=False)
    strategy = Column(String(50), nullable=False)
    total_samples = Column(Integer, default=0)
    valid_schema_rate = Column(Float, default=0.0)
    answer_correctness_rate = Column(Float, default=0.0)
    average_grounding_score = Column(Float, default=0.0)
    average_semantic_similarity = Column(Float, default=0.0)
    average_latency_ms = Column(Float, default=0.0)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db(database_url: str = "sqlite:///./geniq.db"):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
