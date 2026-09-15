"""SCAMX — FinalAnalysisResponse (the single public API response contract)."""
from typing import Optional
from pydantic import BaseModel, Field
from backend.schemas.enums import Modality, ScamCategory, RiskBand, UncertaintyLevel
from backend.schemas.signals import Signal, Evidence
from backend.schemas.analysis import (
    RiskAssessment, AttackChainStep, PotentialHarm,
    SafeAction, OfficialContact, FollowUpQuestion
)


class FinalAnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    input_modality: Modality
    language_detected: str
    processing_time_ms: int

    # ── Core assessment ──────────────────────────────────────
    primary_category: ScamCategory
    secondary_categories: list[ScamCategory] = Field(default_factory=list)
    is_likely_scam: bool
    risk_assessment: RiskAssessment

    # ── Evidence ─────────────────────────────────────────────
    signals: list[Signal] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    attack_chain: list[AttackChainStep] = Field(default_factory=list)
    potential_harm: Optional[PotentialHarm] = None

    # ── Actions ──────────────────────────────────────────────
    immediate_actions: list[SafeAction] = Field(default_factory=list)
    verification_steps: list[SafeAction] = Field(default_factory=list)
    official_contacts: list[OfficialContact] = Field(default_factory=list)
    # Populated only when user is in incident_response mode
    incident_response_actions: list[SafeAction] = Field(default_factory=list)

    # ── Explanation ──────────────────────────────────────────
    explanation: str = ""
    # signal category → normalized strength 0.0–1.0 (for Scam DNA visualization)
    scam_dna: dict[str, float] = Field(default_factory=dict)

    # ── Conversation ─────────────────────────────────────────
    follow_up_questions: list[FollowUpQuestion] = Field(default_factory=list)

    # ── Meta ─────────────────────────────────────────────────
    rag_sources_used: list[str] = Field(default_factory=list)
    degraded_mode: bool = Field(
        False,
        description="True if LLM was unavailable and only rule-based analysis was used"
    )
    schema_version: str = "1.0.0"


class FeedbackRequest(BaseModel):
    analysis_id: str = Field(..., min_length=1, max_length=64)
    was_scam: Optional[bool] = None
    recommendation_helpful: Optional[bool] = None
