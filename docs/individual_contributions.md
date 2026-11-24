# Individual Team Contribution & Role Distribution Document
## Project: Evaluating GenAI for Automatic MCQ Generation (GENIQ)
### MIT Academy of Engineering, Alandi, Pune — Generative AI Lab Practical ESE
### Pathway 2: Research-based Project

---

## 1. Project Roles and Ownership

| Team Member / Role | Core Responsibilities & Modules Owned | Key Deliverables |
|---|---|---|
| **AI/ML Research Engineer** | - SciQ dataset acquisition, missing value filtering, and exploratory analysis.<br>- Embeddings setup with `sentence-transformers/all-MiniLM-L6-v2`.<br>- Experimental pipeline definition (Experiments A, B, C, D). | - `dataset_pipeline.py`<br>- `metrics.py`<br>- `research_runner.py` |
| **Prompt Engineering Specialist** | - Zero-shot, few-shot, and psychometrically-structured prompt templates.<br>- Bloom's taxonomy calibration and distractor plausibility rules.<br>- JSON schema enforcement and Pydantic validation. | - `prompts.py`<br>- `mcq.py` schema<br>- Colab prompt implementation |
| **Backend & Systems Developer** | - FastAPI REST backend service.<br>- PyMuPDF educational PDF text chunking pipeline.<br>- SQLite database schema via SQLAlchemy.<br>- Health check and diagnostics endpoints. | - `main.py`<br>- `document_processor.py`<br>- `db.py` |
| **Frontend & UI/UX Designer** | - Editorial typography-first creative studio aesthetic (GENIQ).<br>- React 18 + Vite + TypeScript application.<br>- Interactive MCQ Generator, Research Lab, Analytics, and Quiz Mode. | - `App.tsx`<br>- `index.css`<br>- `tailwind.config.js` |
| **Academic Documentation & Viva Mentor**| - Google Colab research notebook (`MCQ_Generation_Research_Experiments.ipynb`).<br>- ESE Course Outcome (CO1–CO5) mapping and viva voce question bank.<br>- Technical architecture and methodology documentation. | - `MCQ_Generation_Research_Experiments.ipynb`<br>- `viva_preparation.md`<br>- `architecture.md` |

---

## 2. Evidence of Individual Work and Reproducibility
- All code modules are structured cleanly under modular directories (`backend/app`, `frontend/src`, `research/`, `docs/`).
- Commit and code history reflects phase-by-phase implementation without reliance on simulated mocks or invented results.
- Project is ready for live demonstration and individual technical examination.
