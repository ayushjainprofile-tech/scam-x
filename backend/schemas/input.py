"""SCAMX — Input schemas."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from backend.schemas.enums import Modality, UserState


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Suspicious text to analyze")
    language_hint: Optional[str] = Field(None, pattern=r"^[a-z]{2}$", description="ISO 639-1 language code hint")
    session_context: Optional["SessionContext"] = None


class URLAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=7, max_length=2000)
    session_context: Optional["SessionContext"] = None

    @field_validator("url")
    @classmethod
    def must_be_valid_url(cls, v: str) -> str:
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()


class SessionContext(BaseModel):
    """Passed by client to maintain follow-up conversation state (backend is stateless)."""
    session_id: str = Field(..., min_length=1, max_length=64)
    previous_risk_band: Optional[str] = None
    previous_category: Optional[str] = None
    user_state: UserState = UserState.PREVENTION
    # Answers to follow-up questions
    otp_shared: Optional[bool] = None
    link_clicked: Optional[bool] = None
    money_sent: Optional[bool] = None
    software_installed: Optional[bool] = None
    knows_sender: Optional[bool] = None
    expected_message: Optional[bool] = None


class NormalizedInput(BaseModel):
    """Cleaned, language-detected input ready for analysis pipeline."""
    original_text: str
    normalized_text: str
    language: str = "en"
    modality: Modality = Modality.TEXT
    # Modality-specific confidence (OCR or STT confidence, 1.0 for direct text)
    modality_confidence: float = Field(1.0, ge=0.0, le=1.0)
    # Extracted entities from OCR / preprocessing
    extracted_urls: list[str] = Field(default_factory=list)
    extracted_phone_numbers: list[str] = Field(default_factory=list)
    extracted_amounts: list[str] = Field(default_factory=list)
    # Session context if provided
    session_context: Optional[SessionContext] = None


TextAnalysisRequest.model_rebuild()
URLAnalysisRequest.model_rebuild()
