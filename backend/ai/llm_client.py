"""
SCAMX — LLM Client
Provider-agnostic interface to Gemini.

To swap to a different provider: change ONLY this file.
All other code uses the abstract interface.
"""

import json
import asyncio
from typing import Any, Literal, Optional
from loguru import logger
from backend.config import get_settings

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. LLM calls will fail.")


class LLMError(Exception):
    """Raised when LLM call fails after all retries."""
    pass


class LLMClient:
    """
    Gemini API wrapper with:
    - Structured JSON output
    - Retry with exponential backoff
    - Timeout enforcement
    - Provider isolation (swap here only)
    - Safe logging (never logs prompt content in production)
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        if _GEMINI_AVAILABLE and self._settings.gemini_api_key:
            genai.configure(api_key=self._settings.gemini_api_key)
        self._flash_model = self._settings.gemini_flash_model
        self._pro_model = self._settings.gemini_pro_model

    async def complete_structured(
        self,
        system_prompt: str,
        user_content: str,
        model_tier: Literal["flash", "pro"] = "flash",
        temperature: float = 0.1,
        max_output_tokens: int = 2048,
        fallback_value: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Send a prompt to Gemini and return a validated JSON dict.

        Args:
            system_prompt: Instructions for the model (trusted, not user content)
            user_content: User-provided content wrapped in XML tags by caller
            model_tier: "flash" for speed, "pro" for quality
            temperature: Lower = more deterministic
            fallback_value: Returned on all failures (if None, raises LLMError)
        """
        if not _GEMINI_AVAILABLE or not self._settings.gemini_api_key:
            logger.error("Gemini not available. Returning fallback.")
            if fallback_value is not None:
                return fallback_value
            raise LLMError("Gemini API not configured.")

        model_name = self._flash_model if model_tier == "flash" else self._pro_model
        timeout = (
            self._settings.llm_flash_timeout
            if model_tier == "flash"
            else self._settings.llm_pro_timeout
        )

        full_prompt = f"{system_prompt}\n\n{user_content}"
        delays = [0.5, 1.0, 2.0]

        for attempt, delay in enumerate(delays, start=1):
            try:
                result = await asyncio.wait_for(
                    self._call_gemini(model_name, full_prompt, temperature, max_output_tokens),
                    timeout=timeout,
                )
                logger.debug(f"LLM [{model_tier}] OK on attempt {attempt}")
                return result

            except asyncio.TimeoutError:
                logger.warning(f"LLM [{model_tier}] timeout on attempt {attempt}")
            except Exception as e:
                logger.warning(f"LLM [{model_tier}] error on attempt {attempt}: {type(e).__name__}")

            if attempt < len(delays):
                await asyncio.sleep(delay)

        # All retries exhausted
        if fallback_value is not None:
            logger.error(f"LLM [{model_tier}] failed after {len(delays)} attempts. Using fallback.")
            return fallback_value

        raise LLMError(f"LLM {model_tier} failed after {len(delays)} retries")

    async def _call_gemini(
        self,
        model_name: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, Any]:
        """Make the actual Gemini API call and parse JSON response."""
        # Run the synchronous Gemini call in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._sync_call(model_name, prompt, temperature, max_output_tokens),
        )
        return result

    def _sync_call(
        self,
        model_name: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, Any]:
        """Synchronous Gemini call with JSON response parsing."""
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                response_mime_type="application/json",
            ),
        )
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Parse and return JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Attempt to extract JSON from markdown code block
            import re
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse LLM response as JSON: {e}")
