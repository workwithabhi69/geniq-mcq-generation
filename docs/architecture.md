# Technical Architecture Specification: GENIQ

## 1. System Overview
GENIQ is an experimental Generative AI platform for evaluating automatic Multiple Choice Question (MCQ) generation from educational source materials, aligned with Pathway 2 (Academic Research Project) for the Generative AI Lab Practical End-Semester Examination at MIT Academy of Engineering, Alandi, Pune.

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|   (React 18 + TypeScript + Vite + Tailwind CSS Editorial Minimalist Aesthetic)   |
|   Pages: Landing | MCQ Generator | Research Lab | Analytics | Bank | Quiz Mode    |
+-----------------------------------------------------------------------------------+
                                       |
                                REST API (HTTP)
                                       v
+-----------------------------------------------------------------------------------+
|                               FASTAPI BACKEND                                     |
|  - Endpoints: /api/generate, /api/upload, /api/experiments, /api/questions        |
|  - CORS & Diagnostics Handling                                                    |
+-----------------------------------------------------------------------------------+
        |                                   |                              |
        v                                   v                              v
+------------------+             +--------------------+          +------------------+
| PyMuPDF Pipeline |             |  Prompt Synthesis  |          | SQLite Database  |
| - Text extract   |             |  - Zero-Shot       |          | - Questions Bank |
| - Semantic chunk |             |  - Few-Shot        |          | - Experiments    |
| - Noise filter   |             |  - Structured      |          | - Analytics logs |
+------------------+             +--------------------+          +------------------+
                                            |
                                            v
                                 +--------------------+
                                 | Google GenAI SDK   |
                                 | - Gemini 2.5 Flash |
                                 | - Flash-Lite       |
                                 +--------------------+
                                            |
                                            v
                                 +--------------------+
                                 | Evaluation Engine  |
                                 | - MiniLM Embedding |
                                 | - Grounding Check  |
                                 | - Pydantic Schema  |
                                 +--------------------+
```

## 2. Core Modules
1. **Frontend Presentation**: Black-and-white editorial creative-studio aesthetic, responsive typography (Inter), custom difference-blend cursor, staggered entrance animations.
2. **Document Preprocessing**: PyMuPDF-based text extraction with header/footer cleaning, sentence boundary preservation, and ~300-word overlap chunking.
3. **Generation Architecture**: Strict model independence supporting Gemini Flash variants with exponential backoff and Pydantic validation.
4. **Evaluation Engine**: Semantic similarity via `all-MiniLM-L6-v2`, token-level lexical grounding, exact answer matching, and Cohen's Kappa calculation.
5. **Data Persistence**: SQLite engine via SQLAlchemy with schema migration and export capabilities.
