# Research Methodology: Evaluating GenAI for Automatic MCQ Generation

## 1. Abstract
Multiple Choice Questions (MCQs) are a cornerstone of formative and summative educational assessment. However, authoring high-quality items with plausible distractors, unambiguous stems, and verifiable grounding is labour-intensive. This research investigates the pedagogical effectiveness of modern Generative AI models (Google Gemini 2.5 Flash and Gemini 2.5 Flash-Lite) on the peer-reviewed SciQ science dataset (Welbl et al., 2017). We compare three distinct prompting architectures: Zero-Shot, Few-Shot, and Psychometrically Structured prompting across automated metrics (semantic similarity, token grounding, exact answer matching, Pydantic schema adherence, latency) and human evaluation criteria (1-5 Likert scale, Cohen's Kappa agreement).

## 2. Problem Statement & Hypotheses
Can Generative AI reliably synthesize psychometrically valid multiple-choice questions directly from unstructured scientific text without introducing ungrounded hallucinations or trivial distractors?
- **Hypothesis 1**: Enforcing cognitive scaffolding (Bloom's taxonomy) and verbatim evidence quoting reduces distractor hallucination to under 6% while maintaining 100% schema validity.
- **Hypothesis 2**: Cost-effective Flash-tier models provide competitive question quality with >40% lower latency than larger variants.

## 3. Dataset Characteristics (SciQ)
- **Source**: Allen Institute for Artificial Intelligence (Welbl et al., 2017).
- **Licence**: Creative Commons Attribution-NonCommercial 3.0 (CC BY-NC 3.0).
- **Domains**: Biology, Chemistry, Physics, and Earth Science.
- **Filtering Protocol**: 1,427 items lacking valid support passages were identified and filtered out across splits.
- **Benchmark Sample**: Exactly 200 items randomly sampled from the test split with a fixed random seed (42).

## 4. Controlled Experiments Matrix
1. **Experiment A**: Primary Model (Gemini 2.5 Flash) + Zero-Shot Prompting.
2. **Experiment B**: Primary Model (Gemini 2.5 Flash) + Few-Shot Exemplars.
3. **Experiment C**: Primary Model (Gemini 2.5 Flash) + Psychometrically Structured Prompting.
4. **Experiment D**: Lightweight Model (Gemini 2.5 Flash-Lite) + Psychometrically Structured Prompting.

## 5. Automated & Human Evaluation Pipeline
Automated assessment utilizes sentence embedding vectors via `sentence-transformers/all-MiniLM-L6-v2` for semantic similarity, token-set intersection for context grounding, and strict Pydantic parsing. Human evaluation assesses question clarity, distractor plausibility, factual correctness, and inter-rater reliability via Cohen's Kappa.
