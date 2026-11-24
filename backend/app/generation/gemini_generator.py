"""
GENIQ - Model-Independent Gemini Generation Engine
===================================================
Provides robust integration with Google's Gemini models via google-genai / google-generativeai,
supporting:
- Primary model (e.g. gemini-2.5-flash)
- Lightweight model (e.g. gemini-2.5-flash-lite)
- Configurable environment variable overrides
- Exponential backoff retry handling
- Explicit API key diagnostics (never simulating fake responses)
- Strict JSON parsing, cleanup, and Pydantic validation
"""

import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

from app.schemas.mcq import MCQOutput, PromptStrategyEnum
from app.generation.prompts import build_prompt

logger = logging.getLogger(__name__)

# Configurable model identifiers
DEFAULT_PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gemini-flash-lite-latest")
DEFAULT_LITE_MODEL = os.getenv("LITE_MODEL", "gemini-flash-lite-latest")

class GeminiGenerator:
    """Wrapper for invoking Gemini models with robust validation and error handling."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes the Google GenAI SDK client if API key is provided."""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Real generation calls will return an explicit configuration error.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Initialized Google GenAI Client successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize google.genai Client: {e}")
            self.client = None

    def is_configured(self) -> bool:
        """Returns True if a valid API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_single_mcq(
        self,
        passage: str,
        strategy: str = "structured",
        model_name: Optional[str] = None,
        difficulty: str = "Medium",
        topic: str = "Science",
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> Tuple[Optional[MCQOutput], float, Optional[str]]:
        """
        Generates a single multiple-choice question from an educational passage.
        Returns: (MCQOutput, latency_ms, error_message)
        """
        if not self.is_configured():
            msg = (
                "Gemini API Key is not configured. Please supply a valid GEMINI_API_KEY "
                "in your environment variables or via the application configuration."
            )
            return None, 0.0, msg

        resolved_model = model_name or DEFAULT_PRIMARY_MODEL
        prompt_text = build_prompt(
            strategy=strategy,
            passage=passage,
            difficulty=difficulty,
            topic=topic,
            model_id=resolved_model
        )

        start_time = time.time()
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Invoking {resolved_model} (attempt {attempt}/{max_retries}) using '{strategy}' strategy...")
                
                # Use Google GenAI SDK
                response = self.client.models.generate_content(
                    model=resolved_model,
                    contents=prompt_text,
                    config={
                        "temperature": temperature,
                        "response_mime_type": "application/json"
                    }
                )

                latency_ms = (time.time() - start_time) * 1000
                raw_text = response.text if response and hasattr(response, "text") else ""

                # Parse JSON and validate with Pydantic
                parsed_json = self._extract_json(raw_text)
                if not parsed_json:
                    raise ValueError(f"Failed to parse valid JSON from model response: {raw_text[:200]}")

                # Ensure generation_model & prompt_strategy match
                parsed_json["generation_model"] = resolved_model
                parsed_json["prompt_strategy"] = strategy
                if "difficulty" not in parsed_json or not parsed_json["difficulty"]:
                    parsed_json["difficulty"] = difficulty
                if "topic" not in parsed_json or not parsed_json["topic"]:
                    parsed_json["topic"] = topic

                validated_mcq = MCQOutput(**parsed_json)
                logger.info(f"Successfully generated and validated MCQ in {latency_ms:.1f}ms")
                return validated_mcq, latency_ms, None

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Generation attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    # Exponential backoff
                    sleep_time = 2 ** attempt
                    time.sleep(sleep_time)

        latency_ms = (time.time() - start_time) * 1000
        return None, latency_ms, f"Generation failed after {max_retries} attempts. Last error: {last_error}"

    def _extract_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Strips markdown code blocks and finds the valid JSON block."""
        if not raw_text:
            return None

        # Clean markdown codeblocks
        cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()

        # Try direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Search for first { and last }
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        return None
