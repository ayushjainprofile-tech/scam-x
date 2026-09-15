"""
SCAMX — OCR Processor (Gemini Vision)
Extracts text from screenshots using Gemini Vision API.
Falls back gracefully on API unavailability.
"""

import re
import asyncio
import base64
from dataclasses import dataclass, field
from loguru import logger
from backend.config import get_settings

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False


@dataclass
class OCRResult:
    text: str
    confidence: float  # 0.0 – 1.0
    extracted_urls: list[str] = field(default_factory=list)
    phone_numbers: list[str] = field(default_factory=list)
    ocr_provider: str = "gemini_vision"

_URL_PAT = re.compile(r"https?://[^\s<>\"{}|\\^`\[\]]+|www\.[^\s<>\"{}|\\^`\[\]]+", re.I)
_PHONE_PAT = re.compile(r"(?:\+91|91|0)?[6-9]\d{9}")

_OCR_SYSTEM_PROMPT = """You are an OCR engine analyzing a screenshot.

Extract ALL visible text from the image EXACTLY as it appears.
Pay special attention to:
- URLs and links
- Phone numbers
- Names and organization names
- Amounts and monetary values
- Any warnings or urgent instructions

Return ONLY a JSON object:
{
  "extracted_text": "all text from the image, preserving line breaks with \\n",
  "confidence": 0.9,
  "urls": ["list of all URLs found"],
  "phone_numbers": ["list of phone numbers found"]
}

Do NOT add commentary. Return only the JSON."""


class OCRProcessor:

    def __init__(self) -> None:
        self._settings = get_settings()
        if _GEMINI_AVAILABLE and self._settings.gemini_api_key:
            genai.configure(api_key=self._settings.gemini_api_key)

    async def process(self, image_bytes: bytes, mime_type: str) -> OCRResult:
        """
        Process image bytes through Gemini Vision.
        Returns OCRResult with extracted text and confidence.
        """
        if not _GEMINI_AVAILABLE or not self._settings.gemini_api_key:
            return OCRResult(text="", confidence=0.0, ocr_provider="unavailable")

        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self._sync_ocr, image_bytes, mime_type
                ),
                timeout=20.0,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("OCR timeout after 20s")
            return OCRResult(text="", confidence=0.0)
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return OCRResult(text="", confidence=0.0)

    def _sync_ocr(self, image_bytes: bytes, mime_type: str) -> OCRResult:
        import json
        model = genai.GenerativeModel(
            model_name=self._settings.gemini_flash_model,
            generation_config=genai.GenerationConfig(
                temperature=0.0,
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        )

        image_part = {"mime_type": mime_type, "data": image_bytes}
        response = model.generate_content([_OCR_SYSTEM_PROMPT, image_part])
        raw = response.text.strip()

        try:
            data = json.loads(raw)
        except Exception:
            # Return raw text with low confidence if JSON parsing fails
            return OCRResult(text=raw, confidence=0.4)

        text = str(data.get("extracted_text", "")).strip()
        confidence = float(data.get("confidence", 0.7))

        # Validate URLs from OCR output
        ocr_urls = data.get("urls", [])
        regex_urls = _URL_PAT.findall(text)
        all_urls = list(set(ocr_urls + regex_urls))[:10]

        phones = data.get("phone_numbers", [])
        regex_phones = _PHONE_PAT.findall(text)
        all_phones = list(set(phones + regex_phones))[:5]

        return OCRResult(
            text=text,
            confidence=confidence,
            extracted_urls=all_urls,
            phone_numbers=all_phones,
        )
