# Comprehensive Demonstration Defense Guide: Criteria 1 & 2
## Generative AI Lab Practical End-Semester Examination (Course Code: 22311312L)
### Department of Computer Science and Engineering (AIML), MIT Academy of Engineering, Alandi (D), Pune
### Evaluation Rubric: Section 7, Criterion 1 (CO1) & Criterion 2 (CO2) — 6 Marks Each (12/30 Marks Total)

---

## CRITERION 1: Problem Understanding and Selection of Appropriate Techniques
- **CO Mapping:** CO1 (Bloom's Level L3 – Apply)
- **Mark Allocation:** **6.0 / 6.0 Marks**
- **Evidence Expected During Demonstration (from PDF):**
  > *"Problem is clearly defined; selected deep learning / Generative AI technique is appropriate to the real-world problem; selection is justified."*
- **Performance-Level Descriptor for 5.0–6.0 Marks (Excellent):**
  > *"Complete and convincing evidence; technically sound work; clear explanation, justification and interpretation."*

### 1.1 The Real-World Problem Definition
In modern educational systems, **formative and summative assessment item writing** is a critical operational bottleneck:
1. **Cognitive Fatigue & High Labor Cost:** Authoring high-quality Multiple Choice Questions (MCQs) that adhere to psychometric standards requires domain specialists hours per exam.
2. **The "Distractor Plausibility" Deficit:** Crafting three incorrect options (distractors) that reflect genuine, authentic student misconceptions without being either blatantly obvious (giveaway cues) or inadvertently correct is exceptionally difficult.
3. **Flaws in Naive LLM Generation:** Off-the-shelf generative AI without architectural guardrails causes:
   - **Factual Hallucinations:** Introducing assertions not supported by authoritative course syllabi.
   - **Negative Phrasing & Ambiguity:** Formulating stems with double negatives or multiple defensible answers.
   - **Format Degradation:** Prepending conversational chit-chat or malformed JSON blocks that break automated pipelines.

### 1.2 Target Users & Intended Impact
- **Educators & University Examiners:** Rapidly convert lengthy textbook chapters, lecture notes, or research publications into vetted question banks.
- **Instructional Designers & EdTech Platforms:** Scale personalized assessment generation dynamically.
- **Self-Directed Students:** Generate self-quizzes with instant rationales from their own syllabus notes.

### 1.3 Technique Selection & Scientific Justification
Why use **Pretrained Large Language Models with Structured Psychometric Prompting** instead of Traditional Rule-Based NLP?
- **Why Traditional Rule-Based NLP Fails:** Traditional algorithms (e.g., regex pattern matching, TF-IDF keyword extraction, or noun-phrase masking with WordNet) only produce shallow, verbatim cloze ("fill-in-the-blank") questions. They lack syntactic flexibility and cannot generate plausible, novel conceptual distractors.
- **Why Generative AI Foundation Models Succeed:** Modern LLMs possess deep conceptual representations across scientific domains (Physics, Chemistry, Biology). They can parse complex multi-sentence paragraphs, identify causal relationships, calibrate questions to specific cognitive tiers, and synthesize plausible scientific misconceptions that belong to the exact same semantic category as the correct answer.

### 1.4 Scholarly Literature Review
1. **Welbl, Liu and Gardner (2017) — *Crowdsourcing Multiple Choice Science Questions* (EMNLP):** Established the benchmark dataset (**SciQ**) demonstrating that automated science question generation requires strong passage grounding.
2. **Bloom’s Revised Taxonomy (*Anderson & Krathwohl, 2001*):** Framework used to calibrate question cognitive depth (Easy = Recall, Medium = Application/Conceptual Analysis, Hard = Multi-Step Causal Inference).
3. **Sentence-BERT (*Reimers & Gurevych, 2019*):** Siamese bi-encoder network (`all-MiniLM-L6-v2`) used to objectively evaluate semantic fidelity between generated questions and ground-truth references.

---

## CRITERION 2: Data Processing and Model Implementation
- **CO Mapping:** CO2 (Bloom's Level L3 – Apply)
- **Mark Allocation:** **6.0 / 6.0 Marks**
- **Evidence Expected During Demonstration (from PDF):**
  > *"Demonstrates relevant data preparation and preprocessing; implements/adapts the selected model correctly; explains key development steps and configuration."*
- **Performance-Level Descriptor for 5.0–6.0 Marks (Excellent):**
  > *"Complete and convincing evidence; technically sound work; clear explanation, justification and interpretation."*

### 2.1 Dataset Acquisition, Auditing & Missing Value Handling (SciQ)
- **Dataset Identification:** Official **SciQ dataset** (Allen Institute for AI; Welbl et al., 2017) hosted on Hugging Face (`allenai/sciq`).
- **Data Auditing & Anomaly Detection:**
  - Standard implementations often naively assume all records in SciQ are complete.
  - In GENIQ, we audited the raw dataset of 13,679 records and identified that **1,427 records lacked supporting passages** (1,198 in train, 113 in validation, 116 in test).
  - **Filtering Protocol:** We removed all records with missing or empty `support` passages to ensure that every evaluation item has an authoritative ground truth.
  - **Final Usable Splits:**
    - Train Split: **10,481 records**
    - Validation Split: **887 records**
    - Test Split: **884 records**
- **Reproducible Test Benchmark Extraction:**
  - Sampled a representative subset of **200 test items** with a fixed random seed (`seed=42`).
  - **Passage-Only Evaluation Rule:** During testing, only the `support` passage is passed to the generation model. The original reference question, correct answer, and distractors are strictly withheld, preventing data leakage.
  - Saved in both CSV and JSONL formats at `research/data/sciq_test_benchmark_200.csv`.

### 2.2 Unstructured Educational PDF Preprocessing Pipeline
To support real-world classroom usage, we implemented a complete document processor in `backend/app/preprocessing/document_processor.py`:
1. **Text Stream Extraction:** Uses **PyMuPDF (`fitz` / `pymupdf`)** to extract structured text directly from multi-page educational PDFs (e.g. CBSE Class 12 Physics).
2. **Noise & Artifact Cleansing:** Removes standalone page numbers, header repetitions, and running footers.
3. **Sentence-Boundary Semantic Chunking:** Splits long educational documents into ~250-word chunks with 40-word overlap, strictly respecting sentence terminators (`.`, `!`, `?`) to prevent breaking concepts in mid-sentence.
4. **Scanned PDF Safeguard:** Automatically inspects character density to detect scanned documents lacking extractable text.

### 2.3 Prompt Engineering Architectures Implemented
We implemented and tested three configurable prompt paradigms:
1. **Strategy A (Zero-Shot):** Supplies only the source text, target difficulty, and schema constraints without examples.
2. **Strategy B (Few-Shot):** Injects 2 curated domain exemplars from the SciQ training split illustrating desired formatting and distractor balance before the target passage.
3. **Strategy C (Psychometrically Structured):**
   - Incorporates explicit Bloom's Taxonomy cognitive level instructions.
   - Mandates exactly 4 options (`A`, `B`, `C`, `D`) that are mutually exclusive and grammatically parallel.
   - Mandates distractor plausibility (must represent common scientific misconceptions).
   - Enforces an anti-hallucination constraint: the model must extract and return a verbatim `source_evidence` quote directly from the text.

### 2.4 Model Development & Multi-Engine Hierarchy
We built a model-independent generation architecture supporting:
- **Engine 1 (Primary High-Throughput LPU):** Groq LPU running `openai/gpt-oss-120b`, configured with `temperature = 0.2` and JSON-mode response formatting, producing sub-second generation (~980 ms).
- **Engine 2 (Cloud Alternative):** Google Gemini API (`gemini-flash-lite-latest` via Google GenAI SDK).
- **Engine 3 (Local Offline Fallback):** Syntactic pattern extractor and curated science misconception bank that operates with zero API keys and zero internet access.

### 2.5 Strict Pydantic Data Integrity Schema
All generation outputs are validated using Pydantic v2 (`backend/app/schemas/mcq.py`):
```python
class MCQOptions(BaseModel):
    A: str
    B: str
    C: str
    D: str

class MCQOutput(BaseModel):
    question: str
    options: MCQOptions
    correct_answer: str          # Must be 'A', 'B', 'C', or 'D'
    explanation: str             # Pedagogical rationale
    difficulty: str              # 'Easy', 'Medium', or 'Hard'
    source_evidence: str         # Verbatim textual quote
    topic: str
    generation_model: str
    prompt_strategy: str
```
- Custom validators automatically catch and reject duplicate distractors, missing keys, or empty strings, ensuring **100% schema compliance**.

---

## Demonstration Script for Examiner (Criterion 1 & 2)

### When asked about Criterion 1 (Problem Understanding):
> *"Sir/Ma'am, our project addresses the real-world problem of assessment authoring. Manually writing high-quality MCQs is cognitively exhausting, while naive LLM generation suffers from factual hallucination, give-away distractors, and lack of difficulty calibration. We justified using pretrained Large Language Models benchmarked on the peer-reviewed SciQ science dataset (Welbl et al., 2017) because LLMs possess deep conceptual semantics to generate plausible misconceptions. We calibrated cognitive levels using Bloom's Taxonomy and measured semantic fidelity using Sentence-BERT embeddings."*

### When asked about Criterion 2 (Data Processing & Implementation):
> *"For data preparation, we audited the 13,679-item SciQ dataset and identified that 1,427 records lacked supporting passages. We filtered those out and extracted a reproducible 200-sample benchmark from the test split with seed 42. For user-uploaded PDFs, we built a PyMuPDF pipeline that cleans headers/footers and chunks text into 250-word passages with 40-word overlap. For model implementation, we developed three prompt architectures—zero-shot, few-shot, and psychometrically structured—integrated with Groq's LPU (GPT-OSS-120B) for sub-second generation and validated via strict Pydantic schemas."*
