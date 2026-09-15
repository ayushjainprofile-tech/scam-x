"""SCAMX — Analysis intermediate and final output schemas."""
from typing import Optional
from pydantic import BaseModel, Field
from backend.schemas.enums import (
    RiskBand, ScamCategory, UncertaintyLevel, SignalSeverity, ActionType
)


class RiskAssessment(BaseModel):
    risk_band: RiskBand
    # Internal score — never exposed to end users in API response
    _internal_score: float = 0.0
    confidence: float = Field(..., ge=0.0, le=1.0)
    top_indicators: list[str] = Field(default_factory=list, max_length=5)
    interaction_effects_applied: list[str] = Field(default_factory=list)
    uncertainty_level: UncertaintyLevel
    uncertainty_reason: Optional[str] = None


class AttackChainStep(BaseModel):
    step: int
    description: str  # Must use conditional language ("could allow...", "may result in...")


class PotentialHarm(BaseModel):
    description: str  # Conditional language enforced in prompt
    harm_types: list[str]
    severity: SignalSeverity
    is_conditional: bool = True  # Always True — never claim harm definitely occurred


class SafeAction(BaseModel):
    action: str
    action_type: ActionType
    priority: int = Field(..., ge=1)


class OfficialContact(BaseModel):
    organization: str
    channel: str
    contact: str
    source_tier: int = Field(..., ge=1, le=4)
    source_url: str


class FollowUpQuestion(BaseModel):
    question_id: str
    question: str
    purpose: str
    if_yes_state: str  # e.g. "INCIDENT_RESPONSE"
    if_no_state: str   # e.g. "PREVENTION"


class LLMAnalysisOutput(BaseModel):
    """Raw structured output from LLM — validated before use."""
    classification: dict = Field(default_factory=dict)
    signals: list[dict] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    risk_band: str = "UNCERTAIN"
    uncertainty: dict = Field(default_factory=dict)
    explanation: str = ""
    attack_chain: list[str] = Field(default_factory=list)
    potential_harm: str = ""
    recommended_action: str = ""
    verification_method: str = ""
