"""
SCAMX — AI Analysis Service
Orchestrates all LLM calls: extraction, classification, explanation.
"""

import uuid
from pathlib import Path
from loguru import logger
from backend.ai.llm_client import LLMClient, LLMError
from backend.schemas.signals import Signal, Evidence
from backend.schemas.enums import (
    DetectionSource, SignalSeverity, EvidenceType, ScamCategory
)

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    path = _PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        logger.error(f"Prompt file not found: {path}")
        return ""
    return path.read_text(encoding="utf-8")


class AIAnalysisService:
    """
    Responsible for all LLM interactions in SCAMX.
    Input: normalized text + existing rule signals
    Output: merged signals, classification, explanation
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client
        self._extraction_prompt = _load_prompt("signal_extraction")
        self._classification_prompt = _load_prompt("classification")
        self._explanation_prompt = _load_prompt("explanation")

    async def extract_signals(
        self, normalized_text: str, existing_signal_ids: set[str]
    ) -> list[Signal]:
        """
        Use LLM to detect signals that rules may have missed (paraphrase, Hinglish, context).
        """
        user_content = (
            f"<existing_rule_signals>{', '.join(existing_signal_ids)}</existing_rule_signals>\n\n"
            f"<user_content>{normalized_text}</user_content>"
        )

        fallback: dict = {"signals": [], "extraction_notes": "LLM unavailable"}

        try:
            result = await self._llm.complete_structured(
                system_prompt=self._extraction_prompt,
                user_content=user_content,
                model_tier="flash",
                temperature=0.1,
                fallback_value=fallback,
            )
        except LLMError:
            return []

        llm_signals: list[Signal] = []
        for raw in result.get("signals", []):
            try:
                sig_id = str(raw.get("signal_id", "")).upper()
                if not sig_id.startswith("SIG_"):
                    sig_id = f"SIG_{sig_id}"

                # Skip if rule already detected this
                if sig_id in existing_signal_ids:
                    continue

                confidence = float(raw.get("confidence", 0.5))
                if confidence < 0.50:  # Below minimum threshold
                    continue

                severity_raw = str(raw.get("severity", "MEDIUM")).upper()
                severity = SignalSeverity(severity_raw) if severity_raw in SignalSeverity.__members__ else SignalSeverity.MEDIUM

                llm_signals.append(Signal(
                    signal_id=sig_id,
                    category=str(raw.get("category", "OTHER")),
                    severity=severity,
                    confidence=min(confidence, 0.95),  # Cap LLM confidence
                    detection_source=DetectionSource.LLM,
                    false_positive_risk="MEDIUM",
                ))
            except Exception as e:
                logger.warning(f"Skipping malformed LLM signal: {e}")

        return llm_signals

    async def classify(
        self, normalized_text: str, all_signals: list[Signal]
    ) -> dict:
        """
        Classify scam category from signals + text.
        Returns dict with primary_category, secondary_categories, confidence, is_likely_scam.
        """
        signal_summary = ", ".join(f"{s.signal_id}({s.severity})" for s in all_signals)
        user_content = (
            f"<signals>{signal_summary}</signals>\n\n"
            f"<user_content>{normalized_text}</user_content>"
        )

        fallback = {
            "primary_category": "UNCERTAIN",
            "secondary_categories": [],
            "confidence": 0.0,
            "is_likely_scam": False,
            "reasoning": "Classification unavailable",
        }

        try:
            result = await self._llm.complete_structured(
                system_prompt=self._classification_prompt,
                user_content=user_content,
                model_tier="flash",
                temperature=0.1,
                fallback_value=fallback,
            )
        except LLMError:
            return fallback

        # Validate category values
        valid_categories = {c.value for c in ScamCategory}
        primary = result.get("primary_category", "UNCERTAIN")
        if primary not in valid_categories:
            primary = "UNCERTAIN"

        secondary = [
            c for c in result.get("secondary_categories", [])
            if c in valid_categories and c != primary
        ]

        return {
            "primary_category": primary,
            "secondary_categories": secondary[:3],
            "confidence": float(result.get("confidence", 0.0)),
            "is_likely_scam": bool(result.get("is_likely_scam", False)),
            "reasoning": str(result.get("reasoning", "")),
        }

    async def generate_explanation(
        self,
        normalized_text: str,
        signals: list[Signal],
        evidence: list[Evidence],
        classification: dict,
        rag_context: str = "",
    ) -> dict:
        """
        Generate user-facing explanation with attack chain and harm description.
        """
        signal_summary = "\n".join(
            f"- {s.signal_id}: {s.severity} confidence={s.confidence:.2f}"
            for s in signals[:5]
        )
        evidence_summary = "\n".join(
            f'- "{e.evidence_span}" ({e.signal_id})'
            for e in evidence[:5] if e.verified_in_source
        )
        rag_section = f"\n<reference_guidance>{rag_context}</reference_guidance>" if rag_context else ""

        user_content = (
            f"<category>{classification.get('primary_category', 'UNCERTAIN')}</category>\n"
            f"<signals>\n{signal_summary}\n</signals>\n"
            f"<evidence>\n{evidence_summary}\n</evidence>"
            f"{rag_section}\n\n"
            f"<user_content>{normalized_text[:500]}</user_content>"
        )

        fallback = {
            "explanation": "This message contains indicators commonly associated with scam attempts. Please do not share personal information or make payments without verifying through official channels.",
            "attack_chain": [],
            "potential_harm_description": "If you comply, this could result in financial loss or account compromise.",
            "harm_types": ["financial_loss"],
        }

        try:
            result = await self._llm.complete_structured(
                system_prompt=self._explanation_prompt,
                user_content=user_content,
                model_tier="pro",
                temperature=0.2,
                fallback_value=fallback,
            )
        except LLMError:
            return fallback

        return {
            "explanation": str(result.get("explanation", fallback["explanation"])),
            "attack_chain": [str(s) for s in result.get("attack_chain", [])],
            "potential_harm_description": str(result.get("potential_harm_description", fallback["potential_harm_description"])),
            "harm_types": [str(h) for h in result.get("harm_types", ["financial_loss"])],
        }

    def build_evidence_from_llm_signals(
        self, llm_signals: list[Signal], raw_signal_data: list[dict], source_text: str
    ) -> list[Evidence]:
        """
        Extract and verify evidence spans for LLM-detected signals.
        Verifies each evidence span actually exists in the source text.
        """
        evidence_list: list[Evidence] = []
        signal_evidence_map = {
            raw.get("signal_id", "").upper(): raw.get("evidence_text", "")
            for raw in raw_signal_data
        }

        for sig in llm_signals:
            evidence_text = signal_evidence_map.get(sig.signal_id, "")
            if not evidence_text:
                continue

            # Verify the span actually exists in source
            if evidence_text.lower() in source_text.lower():
                # Find actual span with original casing
                idx = source_text.lower().find(evidence_text.lower())
                actual_span = source_text[idx: idx + len(evidence_text)]
                evd = Evidence(
                    evidence_id=str(uuid.uuid4()),
                    signal_id=sig.signal_id,
                    evidence_span=actual_span[:200],
                    start_char=idx,
                    end_char=idx + len(evidence_text),
                    source_modality="text",
                    evidence_type=EvidenceType.DIRECT_QUOTE,
                    confidence=sig.confidence,
                    verified_in_source=True,
                )
            else:
                # LLM fabricated evidence — mark as inferred, penalize confidence
                evd = Evidence(
                    evidence_id=str(uuid.uuid4()),
                    signal_id=sig.signal_id,
                    evidence_span=evidence_text[:200],
                    source_modality="text",
                    evidence_type=EvidenceType.INFERRED,
                    confidence=sig.confidence * 0.6,
                    verified_in_source=False,
                )

            evidence_list.append(evd)

        return evidence_list
