"""SCAMX — Signal and Evidence schemas."""
from typing import Optional
from pydantic import BaseModel, Field
from backend.schemas.enums import SignalSeverity, EvidenceType, DetectionSource


class Signal(BaseModel):
    signal_id: str = Field(..., description="e.g. SIG_OTP_REQUEST")
    category: str = Field(..., description="e.g. CREDENTIAL_THEFT")
    severity: SignalSeverity
    confidence: float = Field(..., ge=0.0, le=1.0)
    detection_source: DetectionSource
    false_positive_risk: str = Field(..., description="LOW | MEDIUM | HIGH")


class Evidence(BaseModel):
    evidence_id: str
    signal_id: str
    evidence_span: str = Field(..., description="Exact text from source or OCR output")
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    source_modality: str  # text | image | audio
    evidence_type: EvidenceType
    confidence: float = Field(..., ge=0.0, le=1.0)
    verified_in_source: bool = Field(
        ...,
        description="True if evidence_span is an exact substring of the source text"
    )
