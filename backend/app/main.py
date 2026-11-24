"""
GENIQ - FastAPI Application Server
==================================
Exposes REST endpoints for:
- MCQ Generation (PDF upload, text chunking, Gemini invocation)
- Research Experiments runner and metric retrieval
- Question Bank persistence, filtering, and export
- Analytics and benchmark inspection
"""

import os
import io
import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel
from app.schemas.mcq import (
    GenerationRequest,
    GenerationResponse,
    MCQOutput,
    DifficultyEnum,
    PromptStrategyEnum
)
from app.database.db import init_db, QuestionModel, ExperimentRecordModel
from app.generation.gemini_generator import GeminiGenerator
from app.generation.groq_generator import GroqGenerator
from app.generation.offline_generator import LocalOfflineMCQGenerator
from app.preprocessing.document_processor import DocumentProcessor
from app.evaluation.research_runner import ResearchRunner, EXPERIMENTS_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Initialize DB session factory
SessionLocal = init_db(os.getenv("DATABASE_URL", "sqlite:///./geniq.db"))

app = FastAPI(
    title="GENIQ - Educational MCQ Generation & Research API",
    description="Generative AI Research Engine evaluating automated MCQ generation on the SciQ benchmark.",
    version="1.0.0"
)

# CORS Middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

generator = GeminiGenerator()
groq_generator = GroqGenerator()
offline_generator = LocalOfflineMCQGenerator()
doc_processor = DocumentProcessor()

class KeyConfigRequest(BaseModel):
    api_key: str

@app.post("/api/config/key")
def configure_api_key(req: KeyConfigRequest):
    """Allows setting or updating the Gemini API key from the UI."""
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API Key cannot be empty.")
    
    # Update runtime generator and environment
    os.environ["GEMINI_API_KEY"] = key
    generator.api_key = key
    generator._init_client()

    # Persist to .env file
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    try:
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={key}\n")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"GEMINI_API_KEY={key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        logger.warning(f"Could not update .env file: {e}")

    return {
        "success": True,
        "message": "Gemini API key configured successfully.",
        "api_configured": generator.is_configured()
    }

@app.get("/api/health")
def health_check():
    """Returns system status, model configurations and API key diagnostic."""
    return {
        "status": "healthy",
        "api_configured": generator.is_configured(),
        "primary_model": os.getenv("PRIMARY_MODEL", "gemini-flash-lite-latest"),
        "lite_model": os.getenv("LITE_MODEL", "gemini-flash-lite-latest"),
        "database": "sqlite",
        "sciq_benchmark_ready": os.path.exists("research/data/sciq_test_benchmark_200.csv")
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Extracts and chunks educational text from an uploaded PDF document."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    res = doc_processor.extract_text_from_pdf(content)

    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"] or "PDF parsing failed.")

    chunks = doc_processor.chunk_text(res["full_text"], source_reference=file.filename)
    return {
        "filename": file.filename,
        "total_pages": res["total_pages"],
        "is_scanned": res["is_scanned"],
        "total_chunks": len(chunks),
        "chunks": chunks
    }

@app.post("/api/generate", response_model=GenerationResponse)
def generate_mcqs(req: GenerationRequest, db: Session = Depends(get_db)):
    """
    Generates structured Multiple Choice Questions from text passages or educational topics.
    Uses Groq's high-speed inference engine with fallback to local offline NLP engine.
    """
    passage = req.passage
    if not passage or len(passage.strip()) < 20:
        if req.topic:
            passage = f"Educational overview of {req.topic}. Key scientific concepts, definitions, and experimental observations regarding {req.topic}."
        else:
            raise HTTPException(status_code=400, detail="Please provide a valid source passage or educational topic.")

    generated_items: List[MCQOutput] = []
    total_latency = 0.0

    # 1. Primary: Use Groq LPU engine for lightning fast, accurate generation
    if groq_generator.is_configured():
        for i in range(req.num_questions):
            mcq, latency, err = groq_generator.generate_single_mcq(
                passage=passage,
                strategy=req.prompt_strategy.value,
                difficulty=req.difficulty.value,
                topic=req.topic or "Science",
                temperature=req.temperature
            )
            if mcq:
                generated_items.append(mcq)
                total_latency += latency
            else:
                logger.warning(f"Groq item generation failed: {err}")

    # 2. Fallback: If any questions failed or Groq was unavailable, use local generator
    if len(generated_items) < req.num_questions:
        needed = req.num_questions - len(generated_items)
        import time
        start_t = time.time()
        fallback_mcqs = offline_generator.generate_questions(
            passage=passage,
            num_questions=needed,
            difficulty=req.difficulty.value,
            topic=req.topic or "Science",
            prompt_strategy=req.prompt_strategy.value
        )
        total_latency += (time.time() - start_t) * 1000
        generated_items.extend(fallback_mcqs)

    # Persist all generated items into database
    for mcq in generated_items:
        db_item = QuestionModel(
            question_text=mcq.question,
            option_a=mcq.options.A,
            option_b=mcq.options.B,
            option_c=mcq.options.C,
            option_d=mcq.options.D,
            correct_answer=mcq.correct_answer,
            explanation=mcq.explanation,
            source_evidence=mcq.source_evidence,
            source_passage=passage[:500],
            topic=mcq.topic,
            difficulty=mcq.difficulty,
            generation_model=mcq.generation_model,
            prompt_strategy=mcq.prompt_strategy,
            is_saved=True
        )
        db.add(db_item)
    db.commit()

    return GenerationResponse(
        success=True,
        questions=generated_items,
        total_generated=len(generated_items),
        latency_ms=round(total_latency, 1),
        model_used=generated_items[0].generation_model if generated_items else "Groq-GPT-OSS-120B",
        prompt_strategy=req.prompt_strategy.value
    )

@app.get("/api/questions")
def get_questions(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves saved questions from the SQLite Question Bank."""
    q = db.query(QuestionModel)
    if topic:
        q = q.filter(QuestionModel.topic.ilike(f"%{topic}%"))
    if difficulty:
        q = q.filter(QuestionModel.difficulty == difficulty)
    if model:
        q = q.filter(QuestionModel.generation_model.ilike(f"%{model}%"))
    
    items = q.order_by(QuestionModel.id.desc()).all()
    return items

@app.delete("/api/questions/{qid}")
def delete_question(qid: int, db: Session = Depends(get_db)):
    """Deletes a question from the question bank."""
    item = db.query(QuestionModel).filter(QuestionModel.id == qid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(item)
    db.commit()
    return {"success": True, "message": f"Question {qid} deleted."}

@app.delete("/api/questions")
def clear_all_questions(db: Session = Depends(get_db)):
    """Clears all questions from the question bank to start fresh."""
    count = db.query(QuestionModel).delete()
    db.commit()
    return {"success": True, "message": f"Cleared all {count} questions from database."}

@app.get("/api/experiments")
def get_experiments(db: Session = Depends(get_db)):
    """Retrieves experiment configurations and latest run results."""
    results = {}
    for exp_id, meta in EXPERIMENTS_CONFIG.items():
        res_file = os.path.join("research", "results", f"{exp_id}_results.json")
        if os.path.exists(res_file):
            try:
                with open(res_file, "r", encoding="utf-8") as f:
                    results[exp_id] = json.load(f)
            except Exception:
                results[exp_id] = {"summary": {"status": "error_reading_file"}, "config": meta}
        else:
            results[exp_id] = {
                "summary": {
                    "experiment_id": exp_id,
                    "name": meta["name"],
                    "status": "pending",
                    "total_samples": 0
                },
                "config": meta
            }
    return results

@app.post("/api/experiments/run")
def trigger_experiment(exp_id: str, sample_size: int = 5, background_tasks: BackgroundTasks = None):
    """Executes a benchmark experiment run."""
    if exp_id not in EXPERIMENTS_CONFIG:
        raise HTTPException(status_code=400, detail="Unknown experiment identifier")

    benchmark_path = "research/data/sciq_test_benchmark_200.csv"
    if not os.path.exists(benchmark_path):
        raise HTTPException(status_code=400, detail="Benchmark sample not found. Run preprocessing first.")

    runner = ResearchRunner(benchmark_file=benchmark_path)
    res = runner.run_experiment(exp_id, sample_limit=sample_size)
    return res

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Aggregates platform analytics and research metrics."""
    total_q = db.query(QuestionModel).count()
    questions = db.query(QuestionModel).all()

    difficulty_dist = {}
    strategy_dist = {}
    for q in questions:
        difficulty_dist[q.difficulty] = difficulty_dist.get(q.difficulty, 0) + 1
        strategy_dist[q.prompt_strategy] = strategy_dist.get(q.prompt_strategy, 0) + 1

    return {
        "total_generated_questions": total_q,
        "difficulty_distribution": difficulty_dist,
        "strategy_distribution": strategy_dist,
        "api_configured": generator.is_configured(),
        "primary_model": os.getenv("PRIMARY_MODEL", "gemini-flash-lite-latest"),
        "lite_model": os.getenv("LITE_MODEL", "gemini-flash-lite-latest")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
