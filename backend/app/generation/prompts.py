"""
GENIQ - Prompt Engineering Strategies for MCQ Generation
=========================================================
Implements three distinct prompting paradigms:
1. Zero-Shot Prompting
2. Few-Shot Prompting (using domain examples from SciQ train split)
3. Structured Prompting (with rigorous pedagogical constraints & formatting rules)
"""

from typing import Dict, Any, List

SYSTEM_PERSONA = (
    "You are an expert educational psychometrician, scientific researcher, and curriculum designer. "
    "Your objective is to generate rigorous, fair, and pedagogically valid Multiple Choice Questions (MCQs) "
    "strictly grounded in the provided educational passage. "
    "Every question must have exactly one unambiguously correct answer and three plausible, attractive distractors. "
    "You must return exclusively valid JSON conforming strictly to the requested schema."
)

JSON_SCHEMA_INSTRUCTION = """
You MUST output your response as a single, valid JSON object matching this exact schema:
{
  "question": "Clear, concise question stem",
  "options": {
    "A": "Option text",
    "B": "Option text",
    "C": "Option text",
    "D": "Option text"
  },
  "correct_answer": "B",
  "explanation": "Clear explanation referencing facts from the passage",
  "difficulty": "Medium",
  "source_evidence": "Verbatim excerpt from the source passage directly supporting the correct answer",
  "topic": "Science",
  "generation_model": "model_id",
  "prompt_strategy": "strategy_name"
}
Do NOT include markdown formatting wrappers, triple backticks (```json), or conversational preamble. Return pure JSON only.
"""

def get_zero_shot_prompt(passage: str, difficulty: str = "Medium", topic: str = "Science", model_id: str = "gemini-2.5-flash") -> str:
    """Zero-shot prompt: provides only the source passage without examples."""
    prompt = f"""
{SYSTEM_PERSONA}

SOURCE PASSAGE:
\"\"\"
{passage}
\"\"\"

TASK:
Generate exactly ONE multiple choice question based strictly on the source passage above.
Difficulty level: {difficulty}
Topic: {topic}

RULES:
- Exactly four options (A, B, C, D).
- Exactly one correct answer.
- Three plausible, incorrect distractors.
- No duplicate options.
- The correct answer and explanation MUST be directly supported by the passage.
- Set "generation_model" to "{model_id}" and "prompt_strategy" to "zero_shot".

{JSON_SCHEMA_INSTRUCTION}
"""
    return prompt.strip()

def get_few_shot_prompt(passage: str, difficulty: str = "Medium", topic: str = "Science", model_id: str = "gemini-2.5-flash") -> str:
    """Few-shot prompt: provides 2 representative exemplar MCQs from the SciQ dataset."""
    exemplars = """
EXAMPLE 1:
Passage:
"Mesosomes or chondrioids are folded invaginations in the plasma membrane of bacteria that are produced by the chemical fixation techniques used to prepare samples for electron microscopy."
JSON Output:
{
  "question": "What bacterial structures are produced by chemical fixation techniques during preparation for electron microscopy?",
  "options": {
    "A": "Ribosomes",
    "B": "Mesosomes",
    "C": "Plasmids",
    "D": "Flagella"
  },
  "correct_answer": "B",
  "explanation": "According to the passage, mesosomes are folded invaginations in bacteria produced by chemical fixation for electron microscopy.",
  "difficulty": "Medium",
  "source_evidence": "Mesosomes or chondrioids are folded invaginations in the plasma membrane of bacteria that are produced by the chemical fixation techniques",
  "topic": "Biology",
  "generation_model": "reference_exemplar",
  "prompt_strategy": "few_shot"
}

EXAMPLE 2:
Passage:
"Photosynthesis takes place in two stages: the light-dependent reactions and the Calvin cycle. The light-dependent reactions take place in the thylakoid membranes in the granum of the chloroplast, utilizing water and sunlight to synthesize ATP and NADPH."
JSON Output:
{
  "question": "Where do the light-dependent reactions of photosynthesis take place within a chloroplast?",
  "options": {
    "A": "Stroma",
    "B": "Outer membrane",
    "C": "Thylakoid membranes",
    "D": "Mitochondrial matrix"
  },
  "correct_answer": "C",
  "explanation": "The light-dependent reactions take place in the thylakoid membranes located in the granum of the chloroplast.",
  "difficulty": "Medium",
  "source_evidence": "The light-dependent reactions take place in the thylakoid membranes in the granum of the chloroplast",
  "topic": "Biology",
  "generation_model": "reference_exemplar",
  "prompt_strategy": "few_shot"
}
"""

    prompt = f"""
{SYSTEM_PERSONA}

Below are examples of high quality, scientifically accurate multiple-choice questions grounded in educational passages:
{exemplars}

NOW PROCESS THIS TARGET PASSAGE:
\"\"\"
{passage}
\"\"\"

TASK:
Generate exactly ONE multiple choice question following the format and quality of the examples above.
Target Difficulty: {difficulty}
Topic: {topic}
Set "generation_model" to "{model_id}" and "prompt_strategy" to "few_shot".

{JSON_SCHEMA_INSTRUCTION}
"""
    return prompt.strip()

def get_structured_prompt(passage: str, difficulty: str = "Medium", topic: str = "Science", model_id: str = "gemini-2.5-flash") -> str:
    """
    Structured Prompt:
    Incorporates explicit cognitive framing (Bloom's taxonomy), distractor quality rules,
    contextual grounding verification, and strict anti-hallucination guardrails.
    """
    prompt = f"""
{SYSTEM_PERSONA}

PEDAGOGICAL & STRUCTURAL SPECIFICATION:
You must formulate an assessment item adhering to the following strict psychometric criteria:
1. Question Stem:
   - Formulate a clear, direct, unambiguous question stem (prefer interrogative over incomplete sentence).
   - Avoid negative phrasing ('NOT', 'EXCEPT') unless essential.
   - Do NOT simply copy-paste a sentence with a missing blank. Test conceptual understanding.
2. Answer Options (A, B, C, D):
   - Exactly 4 options.
   - Mutually exclusive, grammatically parallel, and homogeneous in length and structure.
   - Avoid give-away clues (e.g. 'All of the above', 'None of the above').
3. Distractor Plausibility:
   - Distractors must represent plausible scientific misconceptions or related domain entities.
   - Distractors must be definitively incorrect according to established scientific fact and the passage.
4. Grounding & Faithfulness:
   - The correct answer must be unambiguously verifiable using the text provided in SOURCE PASSAGE.
   - Include the exact sentence or phrase as `source_evidence`.
   - If the passage lacks sufficient factual substance to support a valid question, do NOT invent facts.
5. Difficulty Calibration ({difficulty}):
   - Easy: Direct recall of clearly stated primary facts or definitions.
   - Medium: Application, comparison, or synthesis of two or more linked ideas from the passage.
   - Hard: Multi-step inference, discerning underlying mechanisms, or evaluating cause-and-effect relationships.

SOURCE PASSAGE:
\"\"\"
{passage}
\"\"\"

METADATA:
- Target Difficulty: {difficulty}
- Domain/Topic: {topic}
- Generation Model ID: {model_id}
- Prompt Strategy: structured

{JSON_SCHEMA_INSTRUCTION}
"""
    return prompt.strip()

def build_prompt(
    strategy: str,
    passage: str,
    difficulty: str = "Medium",
    topic: str = "Science",
    model_id: str = "gemini-2.5-flash"
) -> str:
    """Factory function for selecting the prompt strategy."""
    strat_lower = strategy.lower().strip()
    if strat_lower == "zero_shot":
        return get_zero_shot_prompt(passage, difficulty, topic, model_id)
    elif strat_lower == "few_shot":
        return get_few_shot_prompt(passage, difficulty, topic, model_id)
    elif strat_lower == "structured":
        return get_structured_prompt(passage, difficulty, topic, model_id)
    else:
        raise ValueError(f"Unknown prompt strategy: '{strategy}'. Supported: zero_shot, few_shot, structured")
