"""
GENIQ - Groq Llama 3 MCQ Generator Engine
==========================================
Uses Groq's high-speed inference engine with Llama 3 (llama-3.3-70b-versatile or llama3-8b-8192)
for lightning-fast, grounded MCQ generation.
"""

import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv

load_dotenv()

from app.schemas.mcq import MCQOutput, MCQOptions
from app.generation.prompts import build_prompt

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

class GroqGenerator:
    """Wrapper for invoking Groq LPU with structured MCQ output parsing."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            return
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            logger.info("Initialized Groq client successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_single_mcq(
        self,
        passage: str,
        strategy: str = "structured",
        model_name: Optional[str] = None,
        difficulty: str = "Medium",
        topic: str = "Science",
        temperature: float = 0.2
    ) -> Tuple[Optional[MCQOutput], float, Optional[str]]:
        """Generates a single multiple-choice question using Groq."""
        if not self.is_configured():
            return None, 0.0, "Groq API Key is not configured."

        resolved_model = model_name or DEFAULT_GROQ_MODEL
        prompt_text = build_prompt(
            strategy=strategy,
            passage=passage,
            difficulty=difficulty,
            topic=topic,
            model_id=resolved_model
        )

        start_time = time.time()
        try:
            # Use Groq client with JSON object enforcement
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert psychometrician. You must respond exclusively in valid JSON matching the requested schema."
                    },
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ],
                model=resolved_model,
                temperature=temperature,
                response_format={"type": "json_object"}
            )

            latency_ms = (time.time() - start_time) * 1000
            raw_text = chat_completion.choices[0].message.content or ""

            parsed_json = self._extract_json(raw_text)
            if not parsed_json:
                raise ValueError(f"Could not parse valid JSON from Groq response: {raw_text[:200]}")

            parsed_json["generation_model"] = resolved_model
            parsed_json["prompt_strategy"] = strategy
            if "difficulty" not in parsed_json or not parsed_json["difficulty"]:
                parsed_json["difficulty"] = difficulty
            if "topic" not in parsed_json or not parsed_json["topic"]:
                parsed_json["topic"] = topic

            validated_mcq = MCQOutput(**parsed_json)
            return validated_mcq, latency_ms, None

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Groq generation error: {e}")
            return None, latency_ms, str(e)

    def _extract_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
        return None
