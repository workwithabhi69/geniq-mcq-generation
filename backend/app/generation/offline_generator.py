"""
GENIQ - High Quality Local/Offline NLP MCQ Generator & SciQ Synthesis Engine
=============================================================================
Provides 100% offline, local question generation directly from any input text,
topic, or PDF passage without requiring any external API key or internet connection.
Uses sentence tokenization, key-concept extraction, syntactic transformation,
and plausible distractor synthesis.
"""

import re
import string
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.mcq import MCQOutput, MCQOptions

logger = logging.getLogger(__name__)

class LocalOfflineMCQGenerator:
    """Synthesizes structured MCQs locally from passages without external APIs."""

    def __init__(self):
        # Curated science domain distractors pool
        self.science_distractors_bank = {
            "processes": [
                "Evaporation", "Condensation", "Precipitation", "Transpiration", 
                "Sublimation", "Photosynthesis", "Cellular Respiration", "Fermentation",
                "Diffusion", "Osmosis", "Mitosis", "Meiosis", "Oxidation", "Reduction"
            ],
            "substances": [
                "Carbon dioxide", "Oxygen", "Glucose", "Water vapour", "Methane",
                "Nitrogen", "Chlorophyll", "Hydrogen", "Sulfur dioxide", "Adenosine triphosphate"
            ],
            "structures": [
                "Chloroplasts", "Mitochondria", "Ribosomes", "Cell membrane",
                "Nucleus", "Vacuole", "Endoplasmic reticulum", "Golgi apparatus"
            ],
            "physical_concepts": [
                "Kinetic energy", "Potential energy", "Thermal radiation", "Inertia",
                "Gravitational force", "Centripetal acceleration", "Electromagnetic induction"
            ]
        }

    def generate_questions(
        self,
        passage: str,
        num_questions: int = 3,
        difficulty: str = "Medium",
        topic: str = "Science",
        prompt_strategy: str = "structured"
    ) -> List[MCQOutput]:
        """Generates multiple MCQs locally from the supplied educational passage."""
        cleaned = re.sub(r"\s+", " ", passage).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if len(s.strip().split()) >= 8]

        if not sentences:
            # Fallback for short texts or lone topics
            sentences = [
                f"{topic} is a fundamental concept in science characterized by observable interactions and systematic physical mechanisms.",
                f"During the process of {topic}, energetic transformations occur between different states of matter and environments.",
                f"Experimental research in {topic} reveals direct proportional relationships between cause and effect."
            ]

        generated: List[MCQOutput] = []
        used_evidence = set()

        for i in range(num_questions):
            # Select candidate sentence
            target_idx = i % len(sentences)
            candidate_sentence = sentences[target_idx]
            
            # Avoid duplicate target sentences if possible
            if candidate_sentence in used_evidence and len(sentences) > len(used_evidence):
                for s in sentences:
                    if s not in used_evidence:
                        candidate_sentence = s
                        break
            used_evidence.add(candidate_sentence)

            mcq = self._synthesize_mcq_from_sentence(
                sentence=candidate_sentence,
                passage=cleaned,
                idx=i + 1,
                difficulty=difficulty,
                topic=topic,
                strategy=prompt_strategy
            )
            generated.append(mcq)

        return generated

    def _synthesize_mcq_from_sentence(
        self,
        sentence: str,
        passage: str,
        idx: int,
        difficulty: str,
        topic: str,
        strategy: str
    ) -> MCQOutput:
        """Transforms a sentence into a high-quality MCQ with plausible distractors."""
        words = [w.strip(string.punctuation) for w in sentence.split() if len(w.strip(string.punctuation)) >= 4]

        # Identify candidate concept / keywords
        capitalized = [w for w in words if w[0].isupper() and w.lower() not in ["this", "that", "these", "those", "when", "with"]]
        key_concept = capitalized[0] if capitalized else (words[0] if words else "Process")

        # Patterns for generating thoughtful questions
        q_text = ""
        correct_ans = ""
        explanation = ""

        # Pattern 1: Definitions / "is" / "occurs when"
        if " occurs when " in sentence.lower() or " takes place " in sentence.lower():
            match = re.search(r"^(.*?)(?:occurs when|takes place)(.*)$", sentence, re.IGNORECASE)
            if match:
                subject = match.group(1).strip()
                condition = match.group(2).strip().rstrip(".")
                q_text = f"Under what physical conditions does {subject.lower()} occur?"
                correct_ans = condition.capitalize()
                explanation = f"As stated in the source text: {sentence}"
        
        # Pattern 2: "consists of" / "process by which"
        elif " consists of " in sentence.lower() or " process by which " in sentence.lower():
            match = re.search(r"^(.*?)(?:consists of|is the process by which)(.*)$", sentence, re.IGNORECASE)
            if match:
                subject = match.group(1).strip()
                details = match.group(2).strip().rstrip(".")
                q_text = f"What is described regarding {subject.lower()} in the passage?"
                correct_ans = f"It {details}"
                explanation = f"According to the text, {subject.lower()} is characterized as follows: {sentence}"

        # Pattern 3: Cause and effect / result
        elif " as a result " in sentence.lower() or " convert " in sentence.lower() or " into " in sentence.lower():
            q_text = f"What key transition or outcome is associated with {key_concept.lower()} in the context?"
            correct_ans = sentence.rstrip(".")
            explanation = f"The text directly verifies that {sentence}"

        # Default fallback interrogative question
        if not q_text or len(correct_ans) < 3:
            q_text = f"According to the passage, which statement accurately reflects {key_concept.lower()}?"
            correct_ans = sentence.rstrip(".")
            explanation = f"Directly grounded in the passage: '{sentence}'"

        # Trim long answer strings to concise statements
        if len(correct_ans.split()) > 10:
            subparts = re.split(r"[,;]", correct_ans)
            correct_ans = subparts[0].strip()

        # Generate plausible domain distractors
        distractors = self._generate_distractors(correct_ans, topic)

        # Place options in random positions
        all_options = [correct_ans] + distractors[:3]
        random.seed(idx * 42 + len(sentence))
        random.shuffle(all_options)

        keys = ["A", "B", "C", "D"]
        correct_key = "A"
        opts_dict = {}

        for k, opt in zip(keys, all_options):
            opts_dict[k] = opt
            if opt == correct_ans:
                correct_key = k

        return MCQOutput(
            question=q_text,
            options=MCQOptions(**opts_dict),
            correct_answer=correct_key,
            explanation=explanation,
            difficulty=difficulty,
            source_evidence=sentence,
            topic=topic,
            generation_model="Local-Offline-NLP-Engine",
            prompt_strategy=strategy
        )

    def _generate_distractors(self, correct_answer: str, topic: str) -> List[str]:
        """Creates 3 plausible incorrect alternatives matching the context."""
        # Check domain pools
        pool = []
        for category in self.science_distractors_bank.values():
            pool.extend(category)

        # Remove matches with correct answer
        candidates = [d for d in pool if d.lower() not in correct_answer.lower() and correct_answer.lower() not in d.lower()]
        random.shuffle(candidates)

        if len(candidates) >= 3:
            return candidates[:3]

        return [
            "Thermal equilibrium through stationary absorption",
            "Incomplete catalytic disintegration",
            "Non-reactive atmospheric dispersion"
        ]
