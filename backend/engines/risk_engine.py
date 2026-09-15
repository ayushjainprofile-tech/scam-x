"""
SCAMX — Risk Engine
Aggregates validated signals into a risk assessment.
Deterministic weighted algorithm — no LLM, no randomness.

Algorithm:
  1. Severity-weighted sum of signal confidences
  2. Apply interaction multipliers for known dangerous combinations
  3. Adjust for evidence quality
  4. Adjust for modality confidence (e.g., low OCR confidence reduces score)
  5. Map to risk band via fixed thresholds
  6. Compute uncertainty level
"""

from backend.schemas.signals import Signal, Evidence
from backend.schemas.analysis import RiskAssessment
from backend.schemas.enums import RiskBand, UncertaintyLevel, EvidenceType
from backend.utils.constants import (
    SEVERITY_WEIGHTS,
    RISK_THRESHOLDS,
    INTERACTION_MULTIPLIERS,
    MIN_SIGNALS_FOR_ASSESSMENT,
)


class RiskEngine:

    def compute(
        self,
        signals: list[Signal],
        evidence: list[Evidence],
        modality_confidence: float = 1.0,
    ) -> RiskAssessment:
        """
        Compute a defensible risk assessment from validated signals.
        Every output is traceable to input signals.
        """
        if not signals or len(signals) < MIN_SIGNALS_FOR_ASSESSMENT:
            return RiskAssessment(
                risk_band=RiskBand.UNCERTAIN,
                confidence=0.0,
                top_indicators=[],
                interaction_effects_applied=[],
                uncertainty_level=UncertaintyLevel.INSUFFICIENT_DATA,
                uncertainty_reason="No scam signals detected in the input.",
            )

        # ── Step 1: Base score ───────────────────────────────────────────────
        base_score = sum(
            SEVERITY_WEIGHTS.get(sig.severity, 1.0) * sig.confidence
            for sig in signals
        )

        # ── Step 2: Interaction multipliers ─────────────────────────────────
        signal_ids = {sig.signal_id for sig in signals}
        interactions_applied: list[str] = []

        # Apply the STRONGEST matching interaction only
        best_multiplier = 1.0
        best_label = ""
        for combo, multiplier in INTERACTION_MULTIPLIERS:
            if combo.issubset(signal_ids) and multiplier > best_multiplier:
                best_multiplier = multiplier
                best_label = f"{' + '.join(sorted(combo))} → ×{multiplier}"

        if best_multiplier > 1.0:
            base_score *= best_multiplier
            interactions_applied.append(best_label)

        # ── Step 3: Evidence quality factor ─────────────────────────────────
        if evidence:
            direct_quotes = sum(
                1 for e in evidence
                if e.evidence_type == EvidenceType.DIRECT_QUOTE and e.verified_in_source
            )
            quality_factor = 0.75 + 0.25 * (direct_quotes / len(evidence))
        else:
            quality_factor = 0.70  # Penalize no verified evidence

        # ── Step 4: Modality confidence adjustment ───────────────────────────
        # If OCR/STT was low-confidence, reduce score proportionally
        base_score *= quality_factor * max(0.5, modality_confidence)

        # ── Step 5: Map score → risk band ───────────────────────────────────
        if base_score >= RISK_THRESHOLDS[RiskBand.CRITICAL]:
            risk_band = RiskBand.CRITICAL
        elif base_score >= RISK_THRESHOLDS[RiskBand.HIGH]:
            risk_band = RiskBand.HIGH
        elif base_score >= RISK_THRESHOLDS[RiskBand.MEDIUM]:
            risk_band = RiskBand.MEDIUM
        else:
            risk_band = RiskBand.LOW

        # ── Step 6: Aggregate confidence ────────────────────────────────────
        # Confidence = average signal confidence, weighted by severity
        total_weight = sum(SEVERITY_WEIGHTS.get(s.severity, 1.0) for s in signals)
        agg_confidence = sum(
            SEVERITY_WEIGHTS.get(s.severity, 1.0) * s.confidence for s in signals
        ) / total_weight if total_weight > 0 else 0.5

        # ── Step 7: Uncertainty ──────────────────────────────────────────────
        uncertainty_level = self._compute_uncertainty(signals, agg_confidence)

        # ── Step 8: Top indicators ───────────────────────────────────────────
        sorted_signals = sorted(
            signals,
            key=lambda s: (SEVERITY_WEIGHTS.get(s.severity, 1.0) * s.confidence),
            reverse=True,
        )
        top_indicators = [
            self._human_label(s.signal_id) for s in sorted_signals[:3]
        ]

        result = RiskAssessment(
            risk_band=risk_band,
            confidence=round(agg_confidence, 3),
            top_indicators=top_indicators,
            interaction_effects_applied=interactions_applied,
            uncertainty_level=uncertainty_level,
            uncertainty_reason=self._uncertainty_reason(uncertainty_level),
        )
        # Store internal score (not serialized to API response)
        result._internal_score = round(base_score, 2)
        return result

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _compute_uncertainty(
        self, signals: list[Signal], confidence: float
    ) -> UncertaintyLevel:
        critical_or_high = [
            s for s in signals
            if s.severity in ("CRITICAL", "HIGH") and s.confidence >= 0.75
        ]
        if len(critical_or_high) >= 2 and confidence >= 0.80:
            return UncertaintyLevel.LOW
        if len(signals) >= 2 and confidence >= 0.65:
            return UncertaintyLevel.MODERATE
        if len(signals) >= 1:
            return UncertaintyLevel.HIGH
        return UncertaintyLevel.INSUFFICIENT_DATA

    def _uncertainty_reason(self, level: UncertaintyLevel) -> str | None:
        reasons = {
            UncertaintyLevel.LOW: None,
            UncertaintyLevel.MODERATE: "Several indicators detected with moderate confidence.",
            UncertaintyLevel.HIGH: "Limited signals detected. Treat with caution.",
            UncertaintyLevel.INSUFFICIENT_DATA: "No strong scam indicators found. This does not confirm safety.",
        }
        return reasons.get(level)

    def _human_label(self, signal_id: str) -> str:
        labels = {
            "SIG_OTP_REQUEST": "OTP sharing request detected",
            "SIG_PIN_REQUEST": "PIN request detected",
            "SIG_CVV_REQUEST": "CVV request detected",
            "SIG_PASSWORD_REQUEST": "Password request detected",
            "SIG_URGENCY": "Unusual urgency or time pressure",
            "SIG_THREAT": "Threat of legal action or consequences",
            "SIG_SECRECY": "Instruction to keep message secret",
            "SIG_AUTHORITY": "Claims to be from an authority",
            "SIG_BANK_IMPERSONATION": "Appears to impersonate a bank",
            "SIG_GOVT_IMPERSONATION": "Appears to impersonate a government body",
            "SIG_SUPPORT_IMPERSONATION": "Appears to impersonate customer support",
            "SIG_ADVANCE_FEE": "Advance fee or processing charge requested",
            "SIG_REFUND_MANIPULATION": "Suspicious refund requiring action",
            "SIG_QR_PAYMENT": "QR code payment request",
            "SIG_UPI_REQUEST": "UPI ID solicited",
            "SIG_SCREEN_SHARE": "Remote access software mentioned",
            "SIG_REMOTE_SOFTWARE": "Remote device access requested",
            "SIG_ACCOUNT_SUSPENSION": "Account suspension threat",
            "SIG_LOGIN_PAGE": "Directing to login page",
            "SIG_LOTTERY": "Unsolicited prize or lottery claim",
            "SIG_UNREALISTIC_RETURN": "Unrealistic investment return promised",
            "SIG_JOB_UPFRONT": "Job offer with upfront payment",
            "SIG_KYC_URGENCY": "Urgent KYC update demanded",
            "SIG_SUSPICIOUS_URL": "Suspicious link detected",
            "SIG_LOOKALIKE_DOMAIN": "Domain mimics a known brand",
        }
        return labels.get(signal_id, signal_id.replace("SIG_", "").replace("_", " ").title())
