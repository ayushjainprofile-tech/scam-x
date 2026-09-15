"""
SCAMX — Speech-to-Text Processor (OpenAI Whisper)
Transcribes audio to text for scam analysis.

Important constraints:
- No speaker identification
- No emotion detection
- No deepfake detection (not implemented)
- Low-confidence transcripts are flagged explicitly
"""

import asyncio
import io
from dataclasses import dataclass
from loguru import logger
from backend.config import get_settings

try:
    from openai import AsyncOpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


@dataclass
class STTResult:
    transcript: str
    confidence: float       # Estimated from word-level data, 0.0–1.0
    language_detected: str
    provider: str = "whisper"
    low_confidence_warning: bool = False


class STTProcessor:

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = None
        if _OPENAI_AVAILABLE and self._settings.openai_api_key:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def transcribe(self, audio_bytes: bytes, filename: str) -> STTResult:
        """
        Transcribe audio bytes using OpenAI Whisper.
        Returns STTResult with transcript and confidence.
        """
        if not self._client:
            logger.warning("OpenAI Whisper not configured.")
            return STTResult(
                transcript="",
                confidence=0.0,
                language_detected="en",
                provider="unavailable",
            )

        try:
            result = await asyncio.wait_for(
                self._call_whisper(audio_bytes, filename),
                timeout=45.0,  # Audio processing can take time
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("STT timeout after 45s")
            return STTResult(transcript="", confidence=0.0, language_detected="en")
        except Exception as e:
            logger.error(f"STT failed: {e}")
            return STTResult(transcript="", confidence=0.0, language_detected="en")

    async def _call_whisper(self, audio_bytes: bytes, filename: str) -> STTResult:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        response = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            language=None,  # Auto-detect — handles Hindi, Hinglish, English
        )

        transcript = response.text.strip()
        lang = getattr(response, "language", "en") or "en"

        # Estimate confidence from average word confidence if available
        confidence = 0.8  # Default if no word-level data
        if hasattr(response, "words") and response.words:
            word_confs = [w.get("probability", 0.8) for w in response.words if isinstance(w, dict)]
            if word_confs:
                confidence = sum(word_confs) / len(word_confs)

        low_conf = confidence < 0.6

        return STTResult(
            transcript=transcript,
            confidence=confidence,
            language_detected=lang,
            low_confidence_warning=low_conf,
        )
