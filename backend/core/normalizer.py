"""
SCAMX — Input Normalizer
Cleans text, detects language, masks PII, extracts entities.
Runs BEFORE any LLM or rule engine call.

Security: This is the first defense against unicode-based obfuscation attacks.
"""

import re
import unicodedata
from backend.schemas.input import NormalizedInput
from backend.schemas.enums import Modality

try:
    from langdetect import detect as langdetect_detect, LangDetectException
    _LANGDETECT_AVAILABLE = True
except ImportError:
    _LANGDETECT_AVAILABLE = False


# ── Unicode confusable map (Cyrillic/lookalike → ASCII) ─────────────────────
_CONFUSABLE_MAP: dict[str, str] = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "х": "x", "у": "y", "і": "i", "ѕ": "s", "ԁ": "d",
    "\u200b": "",  # Zero-width space
    "\u200c": "",  # Zero-width non-joiner
    "\u200d": "",  # Zero-width joiner
    "\u202a": "", "\u202b": "", "\u202c": "", "\u202d": "", "\u202e": "",  # Bidi overrides
    "\ufeff": "",  # BOM
}

# ── Regex patterns for entity extraction ────────────────────────────────────
_URL_PATTERN = re.compile(
    r"https?://[^\s<>\"{}|\\^`\[\]]+|www\.[^\s<>\"{}|\\^`\[\]]+",
    re.IGNORECASE,
)
_PHONE_PATTERN = re.compile(
    r"(?:\+91|91|0)?[6-9]\d{9}",  # Indian mobile numbers
)
_AMOUNT_PATTERN = re.compile(
    r"(?:₹|rs\.?|inr)\s*[\d,]+(?:\.\d+)?|\d+\s*(?:lakh|crore|thousand)",
    re.IGNORECASE,
)
_PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Mask Aadhaar numbers (12 digits)
    (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "XXXX-XXXX-XXXX"),
    # Mask PAN card
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "XXXXX####X"),
    # Mask card numbers (13–19 digits)
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "****-****-****-****"),
    # Mask OTPs (4–8 digit codes appearing after OTP-related words)
    (re.compile(r"(?<=otp[:\s])\d{4,8}", re.IGNORECASE), "XXXXXX"),
    (re.compile(r"(?<=code[:\s])\d{4,8}", re.IGNORECASE), "XXXXXX"),
]


class Normalizer:

    def normalize_text(
        self,
        text: str,
        modality: Modality = Modality.TEXT,
        modality_confidence: float = 1.0,
        session_context=None,
    ) -> NormalizedInput:
        """
        Full normalization pipeline:
        1. NFKC unicode normalization
        2. Confusable character mapping
        3. Whitespace normalization
        4. Entity extraction (URLs, phones, amounts)
        5. PII masking in normalized copy
        6. Language detection
        """
        # Step 1: NFKC normalization (handles most unicode tricks)
        cleaned = unicodedata.normalize("NFKC", text)

        # Step 2: Confusable character mapping
        cleaned = "".join(_CONFUSABLE_MAP.get(ch, ch) for ch in cleaned)

        # Step 3: Whitespace normalization
        cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        # Step 4: Entity extraction (before PII masking)
        extracted_urls = _URL_PATTERN.findall(cleaned)
        extracted_phones = _PHONE_PATTERN.findall(cleaned)
        extracted_amounts = _AMOUNT_PATTERN.findall(cleaned)

        # Step 5: PII masking (masked copy used for LLM; original kept for evidence spans)
        masked = cleaned
        for pattern, replacement in _PII_PATTERNS:
            masked = pattern.sub(replacement, masked)

        # Step 6: Language detection
        language = self._detect_language(cleaned)

        return NormalizedInput(
            original_text=text,
            normalized_text=masked,  # LLM sees this masked version
            language=language,
            modality=modality,
            modality_confidence=modality_confidence,
            extracted_urls=extracted_urls[:10],
            extracted_phone_numbers=extracted_phones[:5],
            extracted_amounts=extracted_amounts[:5],
            session_context=session_context,
        )

    def _detect_language(self, text: str) -> str:
        if not _LANGDETECT_AVAILABLE or len(text) < 20:
            return "en"
        try:
            lang = langdetect_detect(text)
            # Map to our supported set
            if lang in ("hi", "mr", "ne"):
                return "hi"
            return "en"
        except Exception:
            return "en"
