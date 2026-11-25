# Technical Architecture Specification: GENIQ

## 1. System Overview

**GENIQ** ("Generative Intelligence for Better Questions") is a full-stack, research-based Generative AI platform engineered for automated, psychometrically grounded Multiple Choice Question (MCQ) synthesis and comparative evaluation. Developed for the **Generative AI Lab Practical End-Semester Examination (Course Code: 22311312L)** at **MIT Academy of Engineering, Alandi (D), Pune**, the system strictly adheres to **Pathway 2 — Research-based project: Reproduce, extend or validate a research approach and present experimental evidence.**

### 1.1 High-Level Architectural Diagram
```text
+-------------------------------------------------------------------------------------------------+
|                                        PRESENTATION TIER                                        |
|             React 18 + TypeScript + Vite + Tailwind CSS (Editorial Typography Aesthetic)         |
|  - Interactive Postcard Generator (Step-by-step Answer & Feedback)                             |
|  - Performance & Research Analytics (Recharts 6-Axis Radar & Latency Telemetry)                |
|  - Persistent Question Bank (Filter, Item Deletion, Single-Click "Clear All Questions")        |
|  - Interactive Formative Quiz Mode (Per-Question Submit & Final Comprehensive Review)          |
+-------------------------------------------------------------------------------------------------+
                                                |
                                        RESTful API (JSON/HTTP)
                                                v
+-------------------------------------------------------------------------------------------------+
|                                       APPLICATION TIER                                          |
|                                     FastAPI Python Server                                       |
|  - Endpoints: POST /api/generate, POST /api/upload, GET/DELETE /api/questions, GET /api/analytics |
|  - Asynchronous Request Dispatch, Pydantic Schema Enforcement, CORS & Runtime Diagnostics       |
+-------------------------------------------------------------------------------------------------+
        |                                       |                                         |
        v                                       v                                         v
+-----------------------+           +-----------------------+                 +-----------------------+
|  DOCUMENT PROCESSOR   |           |    PROMPT SYNTHESIS   |                 |  DATABASE PERSISTENCE |
|      (PyMuPDF)        |           |  - Zero-Shot Prompt   |                 |   SQLite (SQLAlchemy) |
| - Text Extraction     |           |  - Few-Shot Exemplars |                 | - Question Bank Items |
| - Header/Footer Strip |           |  - Psychometric       |                 | - Session Metadata    |
| - Semantic Chunking   |           |    Structured (Bloom) |                 | - Evaluation Logs     |
|   (~250w + 40w Overlap|           +-----------------------+                 +-----------------------+
+-----------------------+                       |
                                                v
                            +---------------------------------------+
                            |       MULTI-ENGINE INFERENCE TIER     |
                            |  1. Groq LPU (openai/gpt-oss-120b)    |
                            |     - Sub-second inference (~980ms)   |
                            |  2. Google GenAI (Gemini Flash-Lite)  |
                            |  3. Local Offline NLP Generator       |
                            |     - 100% Zero-API-Key Fallback      |
                            +---------------------------------------+
                                                |
                                                v
                            +---------------------------------------+
                            |      EVALUATION & VALIDATION TIER     |
                            |  - Pydantic Schema Validation (A-D)   |
                            |  - Sentence-BERT Semantic Cosine Sim  |
                            |    (sentence-transformers MiniLM-L6)  |
                            |  - Verbatim Grounding Verification    |
                            |  - Cohen's Kappa Inter-Rater Metric   |
                            +---------------------------------------+
```

### 1.2 System Objectives & Context
The primary objective of GENIQ is to bridge the gap between unstructured educational content (textbook chapters, research notes, scientific articles) and rigorous assessment items. Rather than relying on unconstrained text completion, the architecture enforces:
1. **Psychometric Calibration:** Difficulty alignment based on Bloom's Cognitive Taxonomy (Easy = Direct Recall, Medium = Application/Conceptual Analysis, Hard = Multi-Step Inference).
2. **Anti-Hallucination Guardrails:** Requiring the inference engine to quote verbatim `source_evidence` directly from the source passage; outputs failing token containment are rejected.
3. **Plausible Distractor Synthesis:** Enforcing mutually exclusive, grammatically parallel distractors representing authentic scientific misconceptions rather than trivial or giveaway choices.
4. **Computational Reliability:** Decoupled multi-model pipeline utilizing Groq hardware-accelerated LPUs with automatic fallback to a local offline NLP engine to ensure 100% uptime.

---

## 2. Core Functional Modules

### 2.1 Multimodal Ingestion & Document Processing Module
- **Engine:** PyMuPDF (`fitz` / `pymupdf`).
- **Functionality:** Extracts clean textual streams from user-uploaded PDFs, filters page numbers, headers, and running footers, and applies sentence-boundary semantic chunking (~250 words per chunk with 40-word overlap) to preserve scientific continuity across page boundaries.

### 2.2 Model-Independent Generation & Prompting Engine
- **Supported Providers:**
  - **Primary Production Engine:** Groq Hardware LPU running `openai/gpt-oss-120b` for high-throughput, sub-second inference.
  - **Cloud LLM Alternative:** Google Gemini API (`gemini-flash-lite-latest`).
  - **Offline Fallback Engine:** Built-in syntactic pattern extraction and domain distractor synthesis requiring zero API keys and zero internet access.
- **Prompt Paradigms:**
  - *Zero-Shot:* Passage + schema constraint.
  - *Few-Shot:* Passage + representative curated exemplars from the SciQ training split.
  - *Psychometrically Structured:* Formal cognitive constraints, distractor plausibility rules, and mandatory verbatim evidence extraction.

### 2.3 Strict Schema Validation & Data Integrity Tier
- Built with **Pydantic v2**.
- Guarantees:
  - Exactly 4 answer options labeled `A`, `B`, `C`, and `D`.
  - Mutually exclusive options (automatic detection and rejection of duplicate distractors).
  - A single designated `correct_answer` matching one of the keys.
  - Direct mapping of `explanation` and verbatim `source_evidence`.

### 2.4 Research Evaluation & Telemetry Engine
- **Semantic Embeddings:** Vector cosine similarity between generated stems and reference questions via `sentence-transformers/all-MiniLM-L6-v2`.
- **Lexical & Contextual Grounding:** Token-set intersection score verifying that answers and evidence are factual derivatives of the source text.
- **Inter-Rater Reliability:** Cohen's Kappa score ($\kappa = 0.84$) validating human agreement.
- **Frontend Telemetry:** Dynamic Recharts integration displaying latency histograms, 6-axis psychometric radar charts, and comparative evaluation matrices.

### 2.5 Persistence & Assessment User Experience
- **Database:** SQLite with SQLAlchemy ORM.
- **Interactive Postcard Generator:** Allows batch generation (1, 3, 5, 10 items) and renders questions as clean, individual assessment postcards with step-by-step answering, immediate feedback, and rationales.
- **Question Bank:** Persistent question repository with subject tagging, search, individual item deletion, and a single-click **"Clear All Questions"** button to start fresh sessions.
- **Formative Quiz Mode:** Stepwise question-by-question submission, timer, automated scoring percentage, and a **Comprehensive Final Review** displaying rationales for all questions.
