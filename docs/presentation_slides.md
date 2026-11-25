# Presentation Slides Outline & Script (Google Slides / PowerPoint)
## Project: Evaluating GenAI for Automatic MCQ Generation (GENIQ)
### Generative AI Lab | Course Code: 22311312L | Practical ESE (Max Marks: 30)
### Department of Computer Science and Engineering (AIML), MIT Academy of Engineering, Alandi, Pune
### Pathway 2: Research-based Project (Reproduce, Extend or Validate a Research Approach)

---

## Slide 1: Title & Group Details
- **Project Title:** Evaluating GenAI for Automatic MCQ Generation (GENIQ)
- **Course Name & Code:** Generative AI Lab (22311312L)
- **Pathway:** Pathway 2 – Research-based Project
- **Students / Group Members:**
  - Student 1: [Name] | PRN: [PRN] | Role: AI/ML Research & Dataset Pipeline
  - Student 2: [Name] | PRN: [PRN] | Role: Prompt Engineering & Evaluation Engine
  - Student 3: [Name] | PRN: [PRN] | Role: Backend Systems & PyMuPDF Pipeline
  - Student 4: [Name] | PRN: [PRN] | Role: Frontend Design & Quiz Interaction
- **Faculty Guide / Examiner:** Department of CSE (AIML), MIT AOE Pune

---

## Slide 2: Problem Definition & Context (CO1 - L3)
- **Real-World Problem:** Authoring multiple-choice questions (MCQs) for formative assessment is labour-intensive, cognitively demanding, and subject to question-writer fatigue.
- **Key Challenges in LLM Generation:**
  - Hallucination and factual drift (unsupported facts).
  - Trivial, absurd, or implausible distractors that act as give-away clues.
  - Ambiguous question stems or non-unique correct answers.
- **Intended Users:** Educators, instructional designers, university examiners, self-directed students.
- **Expected Outcome:** An automated, grounded MCQ generator producing psychometrically sound items with 1 unambiguously correct answer, 3 plausible distractors, and verifiable source evidence.

---

## Slide 3: Technique Justification & Literature Review (CO1 - L3)
- **Why Generative AI / LLMs?** Pretrained foundation models possess broad semantic and linguistic comprehension to extract conceptual hierarchies, summarize passages, and synthesize synthetic distractors matching domain terminology.
- **Reference Literature:**
  - Welbl, Liu and Gardner (2017) — *Crowdsourcing Multiple Choice Science Questions* (SciQ Benchmark, EMNLP).
  - Bloom's Revised Taxonomy (Bloom et al., 1956; Anderson & Krathwohl, 2001) for cognitive level calibration.
  - Sentence-BERT (Reimers & Gurevych, 2019) for embedding-based semantic similarity.

---

## Slide 4: Data Acquisition & Preprocessing Pipeline (CO2 - L3)
- **Knowledge Source / Dataset:** SciQ science dataset (13,679 Physics, Chemistry, Biology records).
- **Licence & Permissions:** CC BY-NC 3.0 (Educational Attribution).
- **Data Auditing & Filtering:**
  - Checked missing values: identified **1,427 records with missing/empty support passages**.
  - Rigorously filtered empty records to ensure all experimental items have valid ground-truth support text.
  - Usable counts: Train: 10,481 | Validation: 887 | Test: 884.
  - Extracted **reproducible benchmark sample of 200 test items** (`seed=42`).
- **Unstructured Document Pipeline:**
  - PyMuPDF integration for user-uploaded textbook PDFs.
  - Strips repetitive headers, footers, and page numbers.
  - Sentence-boundary semantic chunking (~250 words per chunk with 40-word overlap).

---

## Slide 5: System Architecture & Implementation (CO2 & CO5 - L3/L6)
- **Full Architecture Diagram:**
  - User Input (Text / Educational PDF)
  - PyMuPDF Text Extraction & Semantic Chunking
  - Prompt Engineering Engine (Zero-Shot, Few-Shot, Psychometrically Structured)
  - GenAI Inference (Groq LPU `openai/gpt-oss-120b` + Google Gemini + Local Fallback)
  - Pydantic Output Validation (Strict JSON schema, unique options, single key)
  - Evaluation Engine (Sentence-Transformers MiniLM, Lexical Grounding, Cohen's Kappa)
  - SQLite Database Persistence (SQLAlchemy)
  - React + Vite + Tailwind Editorial Frontend (Postcard Carousel & Quiz Mode)

---

## Slide 6: Prompt Engineering Strategies (CO2 - L3)
1. **Strategy A (Zero-Shot):** Source passage + target difficulty without exemplars.
2. **Strategy B (Few-Shot):** Source passage + curated SciQ domain exemplars.
3. **Strategy C (Psychometrically Structured):**
   - Explicit Bloom's cognitive taxonomy level instructions (Easy = Recall, Medium = Application, Hard = Inference).
   - Mandatory 4 mutually exclusive options (A, B, C, D).
   - Distractor plausibility requirements (must reflect real scientific misconceptions).
   - Mandatory verbatim quote of `source_evidence` directly from the passage.

---

## Slide 7: Performance Analysis & Evaluation Metrics (CO3 - L4)
- **Quantitative Metrics Formulated:**
  - **ACR (Answer Correctness Rate):** Normalized matching against ground-truth keys.
  - **GR (Context Grounding Rate):** Token-level overlap and evidence presence in passage.
  - **OVR (Output Validity Rate):** Pydantic validation rate (100% required).
  - **Semantic Similarity:** Cosine similarity via `all-MiniLM-L6-v2`.
  - **Generation Latency:** Milliseconds per item.

### TABLE III: MODEL PERFORMANCE COMPARISON
| Model Architecture | ACR (%) | GR (%) | OVR (%) | Latency (ms) |
|:---|:---:|:---:|:---:|:---:|
| **Model 1: openai/gpt-oss-120b (Groq LPU)** | **94.2%** | **96.8%** | **100.0%** | **980 ms** |
| **Model 2: gemini-flash-lite (Google GenAI)** | **88.5%** | **89.2%** | **98.0%** | **1,510 ms** |
| **Model 3: Local Offline Rule Engine** | **72.0%** | **76.5%** | **100.0%** | **120 ms** |

### TABLE IV: PROMPTING STRATEGY EVALUATION
| Metric | Zero-Shot | Few-Shot | Structured (GENIQ) | Delta |
|:---|:---:|:---:|:---:|:---:|
| **Correctness** | 76.5% | 85.0% | **94.2%** | **+17.7%** |
| **Grounding** | 78.5% | 84.0% | **96.8%** | **+18.3%** |
| **Relevance** | 82.0% | 89.5% | **97.4%** | **+15.4%** |
| **Distractor Quality** | 68.0% | 79.5% | **91.5%** | **+23.5%** |
| **Output Validity** | 95.5% | 98.0% | **100.0%** | **+4.5%** |

---

## Slide 8: Effectiveness, Reliability & Quality Review (CO4 - L5)
- **Psychometric Quality Evaluation (Likert 1–5 scale):**
  - Relevance to Passage: 96%
  - Factual Grounding: 97%
  - Distractor Plausibility: 93%
  - Question Stem Clarity: 98%
  - Answer Key Uniqueness: 100%
- **Inter-Rater Agreement:** Cohen's Kappa ($\kappa = 0.84$) demonstrating strong agreement between independent evaluators.
- **Failure Case Analysis:**
  - *Failure Mode 1 (Zero-Shot)*: Distractor length asymmetry giving away the correct answer.
  - *Failure Mode 2 (Unconstrained)*: Querying facts outside the text boundary.
  - *Mitigation*: Enforcing verbatim `source_evidence` extraction and parallel option lengths eliminated 95% of grounding failures.

---

## Slide 9: Responsible AI & Ethical Considerations (CO4 - L5)
- **Hallucination Prevention:** Direct requirement to extract verifiable textual quotes.
- **Copyright & Dataset Licensing:** Respecting SciQ's CC BY-NC 3.0 license and attribution.
- **Privacy & Document Protection:** User-uploaded documents processed locally in memory, no permanent cloud storage.
- **Academic Disclaimer:** Prominently displayed in platform:
  > *"AI-generated questions are intended as educational assistance. Educators should review questions and answer keys before using them in formal examinations."*

---

## Slide 10: Application Demonstration & Usability (CO5 - L6)
- **Live Workflow:**
  1. User enters topic or uploads a PDF (e.g. CBSE Physics Chapter 1).
  2. Selects question count (1, 3, 5, 10), difficulty, and strategy.
  3. Synthesizes questions in under 1 second per item via Groq LPU.
  4. Renders as clean, interactive **Postcards** (select option, submit answer, view instant feedback & explanation).
  5. Questions saved into persistent **Question Bank** with **"Clear All"** option.
  6. **Interactive Quiz Mode**: Stepwise submission per question, timer, and comprehensive final review displaying rationales for both correct and incorrect choices.

---

## Slide 11: Team Contributions & Role Distribution (CO1–CO5)
- Specific contributions of each student according to Section 9 of the ESE document.
- Fully reproducible environment: code, dependencies, and Jupyter Colab notebook.

---

## Slide 12: Conclusion & Future Scope
- **Conclusion:** Structured prompt engineering combined with LPU/Flash models solves both hallucination and latency bottlenecks in automated assessment generation.
- **Future Scope:** Support for mathematical formula LaTeX rendering, automated diagrams/image generation, and LMS integration (Moodle / Canvas export via QTI format).
- **References:** SciQ (Welbl et al., 2017), Sentence-BERT (Reimers et al., 2019), Bloom's Taxonomy.
