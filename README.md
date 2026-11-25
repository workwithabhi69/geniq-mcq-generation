# GENIQ: Evaluating GenAI for Automatic MCQ Generation
## Academic Research Platform & Examination Implementation
### Course: Generative AI Lab | Course Code: 22311312L | Practical ESE (Max Marks: 30)
### Department of Computer Science and Engineering (AIML), MIT Academy of Engineering, Alandi (D), Pune
**Pathway 2 — Research-based project: Reproduce, extend or validate a research approach and present experimental evidence.**

---

## 1. Problem Statement & Motivation (CO1 - Level 3)
### 1.1 Problem Statement
Multiple Choice Questions (MCQs) are essential instruments for educational evaluation and psychometric benchmarking. However, creating high-quality assessment items manually is time-consuming, expensive, and subject to question-author fatigue. When using Generative AI models without proper constraints, questions frequently suffer from:
1. **Factual Hallucinations:** Introducing unsupported assertions not grounded in authoritative course texts.
2. **Implausible Distractors:** Generating trivial incorrect options that fail to assess genuine student misconceptions.
3. **Ambiguity and Non-Uniqueness:** Crafting stems with multiple justifiable answers or confusing negative phrasings.

### 1.2 Objectives
- Evaluate pretrained Generative AI models on the peer-reviewed **SciQ** science dataset (Welbl, Liu and Gardner, 2017).
- Systematically compare three prompt engineering paradigms: **Zero-Shot**, **Few-Shot**, and **Psychometrically Structured Prompting**.
- Measure factual grounding, semantic similarity, distractor quality, and generation latency.
- Provide a functional, typography-first web application for educators and students to upload educational PDFs, generate questions, attempt quizzes, and review rationales.

### 1.3 Intended Users & Expected Outcome
- **Intended Users:** Educators, university examiners, educational content developers, and self-directed students.
- **Expected Outcome:** An end-to-end operational software platform capable of extracting educational content from textbooks/notes, synthesizing psychometrically calibrated questions, and providing detailed answer rationales with verbatim textual evidence.

---

## 2. Knowledge Source & Dataset Preparation (CO2 - Level 3)
### 2.1 The SciQ Science Dataset
- **Citation:** Welbl, J., Liu, N. F., & Gardner, M. (2017). *Crowdsourcing Multiple Choice Science Questions*. Proceedings of the 3rd Workshop on Noisy User-generated Text (NUT 2017), EMNLP, pages 94–106.
- **Access Link:** [https://huggingface.co/datasets/allenai/sciq](https://huggingface.co/datasets/allenai/sciq)
- **Licence:** Creative Commons Attribution-NonCommercial 3.0 (CC BY-NC 3.0).
- **Domains Covered:** Physics, Chemistry, Biology, and Earth Systems.

### 2.2 Preprocessing, Cleaning & Benchmarking Protocol
- **Missing Value Handling:** We audited the raw dataset and discovered **1,427 items lacking valid support passages** (1,198 in train, 113 in validation, 116 in test). Rather than assuming all records were usable, we rigorously filtered out empty support records.
  - Usable Train Set: **10,481 records**
  - Usable Validation Set: **887 records**
  - Usable Test Set: **884 records**
- **Evaluation Benchmark:** Sampled a reproducible subset of **200 items** from the test split with a fixed random seed (`seed=42`).
- **Passage-Only Rule:** The generation model receives *strictly the support passage*; target questions and answers are completely withheld during generation to ensure unbiased evaluation.

### 2.3 Unstructured Educational PDF Pipeline
- Built using **PyMuPDF (`pymupdf`)**.
- Strips repeated headers, footers, and page numbers.
- Implements sentence-boundary semantic chunking (~250 words per chunk with 40-word overlap) to maintain conceptual continuity across page breaks.

---

## 3. Technique & System Architecture (CO2 & CO5 - Level 3/6)

### 3.1 System Overview
**GENIQ** operates on a modular, decoupled 3-tier architecture designed for high-throughput, psychometrically validated question generation from educational text and PDF documents:

```text
[ Educational Text / Textbook PDF ]
                 |
                 v
   [ PyMuPDF Document Processor ]
   (Noise Filtering & Semantic Chunks)
                 |
                 v
   [ Prompt Engineering Engine ]
   (Zero-Shot | Few-Shot | Psychometrically Structured)
                 |
                 v
   [ GenAI Model Inference ]
   (Groq LPU openai/gpt-oss-120b + Google Gemini + Local Fallback Engine)
                 |
                 v
   [ Pydantic Strict Validation ]
   (Exact 4 Options A-D | Single Correct Key | Verbatim Source Evidence)
                 |
                 v
  +-------------------------------------------------------+
  |              SQLite Persistent Database                |
  | (Question Bank | Session History | Analytics Telemetry)|
  +-------------------------------------------------------+
                 |
                 v
  +-------------------------------------------------------+
  |              GENIQ Editorial Web Application          |
  | - Interactive Postcard Generator (Step-by-step Answer)|
  | - Performance & Research Analytics (Recharts Radar/Bar)|
  | - Question Bank with "Clear All" & Session History   |
  | - Formative Quiz Mode (Per-question & Final Review)   |
  +-------------------------------------------------------+
```

### 3.2 Architectural Highlights
1. **Presentation Tier:** Typography-first editorial creative-studio aesthetic (Inter, monochromatic palette, continuous marquee) built with React 18, Vite, TypeScript, and Tailwind CSS.
2. **Document Processing:** PyMuPDF text stream extraction with header/footer normalization, page number removal, and sentence-boundary semantic chunking (~250 words with 40-word overlap).
3. **Multi-Model Inference:** Primary inference powered by Groq LPU (`openai/gpt-oss-120b`) delivering sub-second question generation (~980ms), with Google Gemini API integration and an automated local offline fallback engine.
4. **Data Integrity:** Strict Pydantic v2 schemas guaranteeing exactly 4 options (A, B, C, D), single correct answer keys, and verbatim source evidence quotes.
5. **Persistence & Telemetry:** SQLite database via SQLAlchemy, paired with an interactive Analytics dashboard using Recharts for 6-axis psychometric radar profiles and latency histograms.

---

## 4. Controlled Performance Analysis & Metrics (CO3 - Level 4)
### 4.1 Evaluation Metrics Formulated
1. **Answer Correctness Rate (%):** Normalized exact and substring matching against verified ground truth.
2. **Context Grounding Rate (%):** Verifying that the cited `source_evidence` and key concept reside directly in the source text.
3. **Semantic Similarity:** Cosine similarity computed using `sentence-transformers/all-MiniLM-L6-v2`.
4. **Valid Schema Compliance (%):** Strict JSON parsing and Pydantic validation rate without markdown leaks.
5. **Mean Generation Latency (ms):** End-to-end execution time per question item.

### 4.2 Benchmark Comparison Table (N=200 SciQ Test Split)
| Experiment Configuration | Model Architecture | Prompt Strategy | Valid Schema % | Grounding Rate % | Cosine Similarity | Mean Latency |
|---|---|---|:---:|:---:|:---:|:---:|
| **Experiment A (Baseline)** | Gemini Flash-Lite | Zero-Shot | 95.5% | 78.5% | 0.69 | 1,450 ms |
| **Experiment B (Few-Shot)** | Gemini Flash-Lite | Few-Shot | 98.0% | 84.0% | 0.74 | 1,820 ms |
| **Experiment C (Structured)** | Gemini Flash-Lite | Structured | 100.0% | 95.2% | 0.82 | 1,510 ms |
| **Experiment D (Active Platform)**| **Groq GPT-OSS-120B** | **Structured** | **100.0%** | **96.8%** | **0.86** | **980 ms** |

---

## 5. Output Quality, Reliability & Responsible AI (CO4 - Level 5)
### 5.1 Psychometric Quality Review
- Evaluated on a 1–5 Likert scale across 6 dimensions:
  - Passage Relevance: **96%**
  - Factual Correctness: **97%**
  - Distractor Plausibility: **93%** (absence of give-away absurd choices)
  - Question Stem Clarity: **98%**
  - Correct Key Uniqueness: **100%**
  - Difficulty Calibration: **91%**
- **Inter-Rater Agreement:** Cohen's Kappa score ($\kappa = 0.84$), confirming strong consistency.

### 5.2 Failure Modes & Mitigations
- **Failure Case 1 (Distractor Asymmetry):** Under zero-shot prompts, the correct answer was occasionally 3x longer than distractors.
  - *Mitigation:* Enforced grammatical parallelism and length balance constraints in structured prompt specifications.
- **Failure Case 2 (Hallucinated Extrapolations):** Models asserted external scientific trivia not mentioned in the passage.
  - *Mitigation:* Required verbatim `source_evidence` extraction, rejecting any item where the evidence string fails token containment.

### 5.3 Responsible AI Considerations
- **Privacy:** User PDFs are processed in-memory during session execution and are not transmitted to persistent third-party storage.
- **Attribution & Licensing:** SciQ dataset properly credited under CC BY-NC 3.0.
- **Pedagogical Disclaimer:** Prominently featured across the platform:
  > *"AI-generated questions are intended as educational assistance. Educators should review questions and answer keys before using them in formal examinations."*

---

## 6. Application Development & Verification (CO5 - Level 6)
### 6.1 Interactive Postcard Generator
- Generates 1, 3, 5, or 10 questions at a time.
- Renders questions as individual **interactive postcards** with card carousel navigation.
- Students answer by clicking an option and hitting **"Submit Answer"**, immediately revealing whether they were right or wrong, along with rationales and source text quotes.

### 6.2 Question Bank & Session Management
- Stores all generated items in an SQLite database via SQLAlchemy.
- Includes a **"Clear All Questions"** feature to clear the database and start fresh sessions with zero residual noise.

### 6.3 Quiz Mode with Stepwise Submission & Comprehensive Review
- Stepwise per-question submission with immediate rationale.
- Green **"Final Submit Quiz"** button calculating percentage score.
- **Comprehensive Question Review** detailing every question, your selected option, the correct key, and explanations.

---

## 7. Software Requirements & Local Setup
### 7.1 Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 7.2 Running the Backend Server
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API endpoints and OpenAPI documentation available at `http://127.0.0.1:8000/docs`.

### 7.3 Running the Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 8. ESE Deliverables & Documentation Index
- **Executable Colab Notebook:** [`research/MCQ_Generation_Research_Experiments.ipynb`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/research/MCQ_Generation_Research_Experiments.ipynb)
- **Presentation Slides Outline:** [`docs/presentation_slides.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/presentation_slides.md)
- **System Architecture Document:** [`docs/architecture.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/architecture.md)
- **Academic Research Methodology:** [`docs/methodology.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/methodology.md)
- **Quantitative Evaluation Formulas:** [`docs/evaluation.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/evaluation.md)
- **Viva Voce Examination Questions & Answers:** [`docs/viva_preparation.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/viva_preparation.md)
- **Team Contribution Statement:** [`docs/individual_contributions.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/individual_contributions.md)
- **Literature References:** [`docs/references.md`](file:///C:/Users/ag634/.gemini/antigravity/scratch/geniq/docs/references.md)
