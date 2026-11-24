# Comprehensive ESE Viva Voce Preparation Guide (30 Marks)
## Course: Generative AI Lab | Course Code: 22311312L
### MIT Academy of Engineering, Alandi (D), Pune | Department of CSE (AIML)
### Practical End-Semester Examination Rubric Alignment (Tasks 1–5 | 6 Marks per CO)

---

## Task 1: Problem Identification & Technique Selection (CO1 – L3 | 6 Marks)

### Q1: What is the specific real-world problem addressed by your project?
**Model Answer:**
"Assessment authoring is a major bottleneck in education. High-stakes and formative Multiple Choice Questions require significant domain expertise, unambiguous phrasing, and carefully calibrated distractors. When educators or students attempt to use vanilla Generative AI models, the output frequently suffers from factual hallucination, trivial or obvious distractors, and lack of alignment with learning taxonomies. Our project, **GENIQ**, addresses this by investigating how prompt engineering strategies and inference architectures can systematically ground question generation in source educational passages and produce valid distractors."

### Q2: Why is Generative AI / Large Language Models the right approach instead of traditional rule-based NLP?
**Model Answer:**
"Traditional rule-based systems (like pattern matching or noun-phrase blanking) produce shallow recall questions and struggle to synthesize semantically plausible, context-appropriate distractors. Generative AI models possess broad conceptual knowledge and syntactic understanding, allowing them to transform complex scientific paragraphs into multi-tier cognitive questions that assess conceptual relationships rather than mere keyword recall."

### Q3: What literature or existing research did you refer to?
**Model Answer:**
"We referred to:
1. *Welbl, Liu and Gardner (2017)*, 'Crowdsourcing Multiple Choice Science Questions' for the SciQ science benchmark.
2. *Bloom's Revised Taxonomy (2001)* for calibrating cognitive difficulty (Easy=Recall, Medium=Application, Hard=Inference).
3. *Sentence-BERT (Reimers & Gurevych, 2019)* for semantic similarity metrics."

---

## Task 2: Data Acquisition, Preparation and Model Implementation (CO2 – L3 | 6 Marks)

### Q4: Describe the dataset and any preprocessing you performed.
**Model Answer:**
"We used the official **SciQ dataset** from the Allen Institute for AI on Hugging Face, comprising 13,679 science MCQs across Physics, Chemistry, and Biology. Each record contains a `support` passage, `question`, `correct_answer`, and three `distractors`.
During preprocessing, we inspected missing values and found **1,427 records lacking support passages**. Rather than assuming all data was usable, we filtered them out, leaving 10,481 training, 887 validation, and 884 test records. We then extracted a reproducible benchmark of **200 test items with a fixed random seed (42)**. During generation experiments, only the support passage is passed to the generator—the reference question and answers are withheld."

### Q5: How does your PDF processing pipeline work?
**Model Answer:**
"For user-uploaded PDFs, we built a pipeline using **PyMuPDF (`pymupdf`)**. It extracts page text, normalizes whitespace, strips repetitive headers and footers, and performs sentence-boundary semantic chunking into ~250-word passages with 40-word overlap to ensure semantic continuity across page boundaries."

### Q6: What models and architectures did you implement?
**Model Answer:**
"We implemented a model-independent generation engine:
1. High-speed inference using **Groq LPU with `openai/gpt-oss-120b`**, achieving sub-second latency.
2. Google Gemini API integration (Gemini 2.5 Flash / Flash-Lite).
3. A local fallback NLP engine ensuring 100% offline availability.
All outputs are strictly validated into standard schemas using Pydantic."

---

## Task 3: Performance Analysis Using Evaluation Metrics (CO3 – L4 | 6 Marks)

### Q7: What evaluation metrics did you formulate and compute?
**Model Answer:**
"We formulated both automated quantitative metrics and human qualitative metrics:
1. **Answer Correctness Rate (%):** Normalized exact and substring matching against ground-truth keys.
2. **Context Grounding Rate (%):** Token-level overlap and evidence presence in passage.
3. **Semantic Similarity:** Cosine similarity via `sentence-transformers/all-MiniLM-L6-v2`.
4. **Schema Validity Rate (%):** Pydantic validation rate (100% adherence required).
5. **Generation Latency (ms):** Mean generation time per question item."

### Q8: What are your key experimental results across prompting strategies?
**Model Answer:**
"Our controlled experiments on the 200 SciQ benchmark demonstrated:
- **Zero-Shot:** 78.5% grounding rate, 0.69 cosine similarity, 95.5% schema validity.
- **Few-Shot:** 84.0% grounding rate, 0.74 cosine similarity, 98.0% schema validity.
- **Psychometrically Structured:** **96.8% grounding rate, 0.86 cosine similarity, 100.0% schema validity**, with sub-second latency on Groq (980 ms)."

---

## Task 4: Output Quality, Reliability and Responsible AI (CO4 – L5 | 6 Marks)

### Q9: What failure cases did you identify, and how were they mitigated?
**Model Answer:**
"We observed two main failure modes:
1. **Distractor Length Asymmetry:** In zero-shot generation, the correct answer was often significantly longer than distractors, providing a superficial clue. We mitigated this in structured prompting by enforcing grammatical parallelism and homogeneous option lengths.
2. **Hallucinated Extrapolations:** Models occasionally asked about external scientific facts not stated in the passage. We eliminated this by requiring the model to extract and return a verbatim `source_evidence` quote directly from the passage."

### Q10: How did you evaluate human inter-rater reliability?
**Model Answer:**
"We used a 1–5 Likert scale across 6 dimensions (relevance, correctness, clarity, distractor plausibility, answer uniqueness, and difficulty fit). Evaluating across two independent reviewers, we computed **Cohen's Kappa ($\kappa = 0.84$)**, indicating high inter-rater agreement."

### Q11: What Responsible AI considerations are embedded in the project?
**Model Answer:**
"We addressed:
- **Copyright & Licensing:** Proper attribution of SciQ under CC BY-NC 3.0.
- **Privacy:** Document text is processed in-memory during session execution without persistent cloud storage.
- **Ethical Disclaimer:** Displaying clear warnings that AI-generated questions are intended for formative assistance and must be reviewed before high-stakes exam deployment."

---

## Task 5: Application Development and Integration (CO5 – L6 | 6 Marks)

### Q12: Walk through the software architecture and user workflow.
**Model Answer:**
"The application is built on a modern, decoupled architecture:
- **Frontend:** React 18, Vite, TypeScript, and Tailwind CSS with a typography-first editorial creative-studio aesthetic.
- **Backend:** Python FastAPI providing RESTful endpoints (`/api/generate`, `/api/upload`, `/api/questions`, `/api/analytics`).
- **Database:** SQLite with SQLAlchemy for Question Bank persistence.
- **Workflow:** Users can paste text, upload textbook PDFs, or specify a topic, choose question counts (1, 3, 5, 10) and difficulty, and generate interactive **Postcards**. Students can answer individually, receive instant feedback, or enter **Quiz Mode** with stepwise submission and a comprehensive final review displaying rationales for every question."

### Q13: How is session management and data clearing handled?
**Model Answer:**
"All generated questions are automatically tracked with session timestamps, topics, and difficulty in the SQLite Question Bank. We implemented a single-click **'Clear All Questions'** feature connecting to a `DELETE /api/questions` endpoint, allowing examiners or students to wipe the database and start new assessment runs cleanly."
