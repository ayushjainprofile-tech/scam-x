import pytest
from backend.engines.risk_engine import RiskEngine
from backend.engines.safety_engine import SafetyEngine
from backend.schemas.signals import Signal, Evidence
from backend.schemas.enums import RiskBand, UncertaintyLevel, EvidenceType

@pytest.fixture
def risk_engine():
    return RiskEngine()

@pytest.fixture
def safety_engine():
    return SafetyEngine()

def test_empty_signals_returns_uncertain(risk_engine):
    assessment = risk_engine.compute(signals=[], evidence=[])
    assert assessment.risk_band == RiskBand.UNCERTAIN
    assert assessment.confidence == 0.0
    assert assessment.uncertainty_level == UncertaintyLevel.INSUFFICIENT_DATA

def test_single_high_signal_risk_calculation(risk_engine):
    sig = Signal(
        signal_id="SIG_OTP_REQUEST",
        category="AUTHENTICATION",
        confidence=0.9,
        severity="CRITICAL",
        description="OTP request detected",
        matched_text="Share your OTP",
        rule_or_llm="RULE"
    )
    ev = Evidence(
        evidence_type=EvidenceType.DIRECT_QUOTE,
        content="Share your OTP",
        verified_in_source=True
    )
    assessment = risk_engine.compute(signals=[sig], evidence=[ev])
    assert assessment.risk_band in (RiskBand.HIGH, RiskBand.CRITICAL)
    assert assessment.confidence >= 0.7
    assert "OTP sharing request detected" in assessment.top_indicators

def test_interaction_multiplier_applied(risk_engine):
    sig1 = Signal(
        signal_id="SIG_URGENCY",
        category="URGENCY",
        confidence=0.9,
        severity="HIGH",
        description="Urgency detected",
        matched_text="within 2 hours",
        rule_or_llm="RULE"
    )
    sig2 = Signal(
        signal_id="SIG_ACCOUNT_SUSPENSION",
        category="THREAT",
        confidence=0.85,
        severity="HIGH",
        description="Account suspension threat",
        matched_text="account blocked",
        rule_or_llm="RULE"
    )
    assessment = risk_engine.compute(signals=[sig1, sig2], evidence=[])
    assert len(assessment.interaction_effects_applied) > 0
    assert assessment.risk_band in (RiskBand.HIGH, RiskBand.CRITICAL)

def test_safety_policy_generator_critical_risk(safety_engine, risk_engine):
    sig = Signal(
        signal_id="SIG_OTP_REQUEST",
        category="AUTHENTICATION",
        confidence=0.95,
        severity="CRITICAL",
        description="OTP request",
        matched_text="OTP 123456",
        rule_or_llm="RULE"
    )
    assessment = risk_engine.compute(signals=[sig], evidence=[])
    policy = safety_engine.generate(
        risk_assessment=assessment,
        signals=[sig],
        primary_category="ACCOUNT_TAKEOVER",
        session_context=None
    )
    assert len(policy.immediate_actions) > 0
    assert len(policy.verification_steps) > 0
    # Mandatory helpline check for critical risk
    helpline_contacts = [c for c in policy.official_contacts if "1930" in c.contact_value or "1930" in c.label]
    assert len(helpline_contacts) > 0
