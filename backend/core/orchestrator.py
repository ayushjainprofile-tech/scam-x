"""
SCAMX — Central Analysis Orchestrator
The SINGLE entry point for all analysis.

Pipeline (in order):
  1. Validate input
  2. Normalize (unicode, PII mask, entity extract)
  3. Rule engine (deterministic, fast)
  4. URL engine (if URLs present)
  5. LLM signal extraction (semantic, catches what rules miss)
  6. Merge + deduplicate signals
  7. Build evidence (with span verification)
  8. Classify scam category
  9. Risk engine (weighted algorithm)
 10. Safety engine (deterministic policy floor)
 11. Generate explanation (LLM + RAG context if available)
 12. Response safety check
 13. Return FinalAnalysisResponse

Invariants:
  - Orchestrator NEVER calls LLM for risk decisions
  - Safety engine ALWAYS runs after LLM
  - Evidence spans ALWAYS verified before display
  - Every step is logged with metadata (never with user content in production)
"""

import uuid
import time
from datetime import datetime, timezone
from loguru import logger
from backend.core.normalizer import Normalizer
from backend.engines.rule_engine import RuleEngine
from backend.engines.risk_engine import RiskEngine
from backend.engines.safety_engine import SafetyEngine
from backend.ai.llm_client import LLMClient
from backend.ai.analysis_service import AIAnalysisService
from backend.schemas.input import NormalizedInput
from backend.schemas.signals import Signal, Evidence
from backend.schemas.enums import (
    Modality, ScamCategory, RiskBand, SignalSeverity,
    UncertaintyLevel, UserState, ActionType, DetectionSource
)
from backend.schemas.analysis import (
    RiskAssessment, AttackChainStep, PotentialHarm, SafeAction
)
from backend.schemas.response import FinalAnalysisResponse

try:
    from backend.multimodal.url_processor import URLProcessor
    _URL_PROCESSOR_AVAILABLE = True
except ImportError:
    _URL_PROCESSOR_AVAILABLE = False

try:
    from backend.rag.retriever import RAGRetriever
    _RAG_AVAILABLE = True
except ImportError:
    _RAG_AVAILABLE = False


class AnalysisOrchestrator:
    """
    Stateless analysis pipeline.
    All state is passed in and returned — nothing is stored between calls.
    """

    def __init__(self) -> None:
        self._normalizer = Normalizer()
        self._rule_engine = RuleEngine()
        self._risk_engine = RiskEngine()
        self._safety_engine = SafetyEngine()
        self._llm_client = LLMClient()
        self._ai_service = AIAnalysisService(self._llm_client)
        self._url_processor = URLProcessor() if _URL_PROCESSOR_AVAILABLE else None
        self._rag_retriever = RAGRetriever() if _RAG_AVAILABLE else None

    async def analyze_text(
        self,
        text: str,
        language_hint: str | None = None,
        session_context=None,
    ) -> FinalAnalysisResponse:
        """Full analysis pipeline for text input."""
        t0 = time.monotonic()
        analysis_id = str(uuid.uuid4())
        logger.info(f"[{analysis_id}] Text analysis started. len={len(text)}")

        # ── 1. Normalize ─────────────────────────────────────────────────────
        normalized = self._normalizer.normalize_text(
            text=text,
            modality=Modality.TEXT,
            session_context=session_context,
        )

        result = await self._run_pipeline(normalized, analysis_id, t0)
        logger.info(
            f"[{analysis_id}] Complete. risk={result.risk_assessment.risk_band} "
            f"signals={len(result.signals)} time={result.processing_time_ms}ms"
        )
        return result

    async def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        session_context=None,
    ) -> FinalAnalysisResponse:
        """OCR pipeline then shared analysis."""
        from backend.multimodal.ocr_processor import OCRProcessor
        t0 = time.monotonic()
        analysis_id = str(uuid.uuid4())
        logger.info(f"[{analysis_id}] Image analysis started.")

        ocr = OCRProcessor()
        ocr_result = await ocr.process(image_bytes, mime_type)

        normalized = self._normalizer.normalize_text(
            text=ocr_result.text,
            modality=Modality.IMAGE,
            modality_confidence=ocr_result.confidence,
            session_context=session_context,
        )
        # Merge extracted entities from OCR
        normalized.extracted_urls.extend(ocr_result.extracted_urls)
        normalized.extracted_phone_numbers.extend(ocr_result.phone_numbers)

        result = await self._run_pipeline(normalized, analysis_id, t0)
        return result

    async def analyze_url(
        self,
        url: str,
        session_context=None,
    ) -> FinalAnalysisResponse:
        """URL-focused analysis using static domain analysis."""
        t0 = time.monotonic()
        analysis_id = str(uuid.uuid4())

        normalized = self._normalizer.normalize_text(
            text=url,
            modality=Modality.URL,
            session_context=session_context,
        )
        normalized.extracted_urls = [url]

        result = await self._run_pipeline(normalized, analysis_id, t0)
        return result

    async def analyze_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        session_context=None,
    ) -> FinalAnalysisResponse:
        """STT pipeline then shared analysis."""
        from backend.multimodal.stt_processor import STTProcessor
        t0 = time.monotonic()
        analysis_id = str(uuid.uuid4())

        stt = STTProcessor()
        stt_result = await stt.transcribe(audio_bytes, filename)

        normalized = self._normalizer.normalize_text(
            text=stt_result.transcript,
            modality=Modality.AUDIO,
            modality_confidence=stt_result.confidence,
            session_context=session_context,
        )

        result = await self._run_pipeline(normalized, analysis_id, t0)
        return result

    # ── Core pipeline (shared by all modalities) ──────────────────────────────

    async def _run_pipeline(
        self,
        normalized: NormalizedInput,
        analysis_id: str,
        t0: float,
    ) -> FinalAnalysisResponse:
        degraded_mode = False

        # ── 2. Rule engine ───────────────────────────────────────────────────
        rule_signals, rule_evidence = self._rule_engine.detect(
            normalized.normalized_text,
            source_modality=normalized.modality.value,
        )
        rule_signal_ids = {s.signal_id for s in rule_signals}
        logger.debug(f"Rule engine: {len(rule_signals)} signals")

        # ── 3. URL engine ────────────────────────────────────────────────────
        url_signals: list[Signal] = []
        url_evidence: list[Evidence] = []
        if normalized.extracted_urls and self._url_processor:
            for url in normalized.extracted_urls[:3]:
                u_sigs, u_evd = self._url_processor.analyze(url)
                url_signals.extend(u_sigs)
                url_evidence.extend(u_evd)

        # ── 4. LLM signal extraction ─────────────────────────────────────────
        llm_signals: list[Signal] = []
        llm_evidence: list[Evidence] = []
        try:
            llm_signals = await self._ai_service.extract_signals(
                normalized.normalized_text,
                existing_signal_ids=rule_signal_ids,
            )
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}. Using rules-only.")
            degraded_mode = True

        # ── 5. Merge signals ─────────────────────────────────────────────────
        all_signals = self._merge_signals(rule_signals, llm_signals, url_signals)

        # ── 6. Classify ──────────────────────────────────────────────────────
        classification = {
            "primary_category": ScamCategory.UNCERTAIN,
            "secondary_categories": [],
            "confidence": 0.0,
            "is_likely_scam": False,
        }
        try:
            raw_class = await self._ai_service.classify(
                normalized.normalized_text, all_signals
            )
            classification = raw_class
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")
            # Infer basic category from signals
            classification = self._infer_category_from_signals(all_signals)

        # ── 7. Build all evidence ────────────────────────────────────────────
        all_evidence = rule_evidence + url_evidence + llm_evidence

        # ── 8. Risk engine ───────────────────────────────────────────────────
        risk = self._risk_engine.compute(
            all_signals, all_evidence, normalized.modality_confidence
        )

        # ── 9. Safety engine ─────────────────────────────────────────────────
        user_state = UserState.PREVENTION
        if normalized.session_context:
            user_state = normalized.session_context.user_state

        safety_output = self._safety_engine.get_actions(
            signals=all_signals,
            category=classification["primary_category"],
            risk_band=risk.risk_band,
            user_state=user_state,
            session_context=normalized.session_context,
        )

        # ── 10. RAG retrieval (conditional) ──────────────────────────────────
        rag_context = ""
        rag_sources: list[str] = []
        if self._rag_retriever and self._should_call_rag(classification, risk):
            try:
                rag_docs = await self._rag_retriever.retrieve(
                    category=classification["primary_category"],
                    language=normalized.language,
                )
                rag_context = "\n\n".join(d["content"] for d in rag_docs[:2])
                rag_sources = [d["doc_id"] for d in rag_docs[:2]]
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        # ── 11. Generate explanation ──────────────────────────────────────────
        explanation_data = {
            "explanation": self._default_explanation(risk.risk_band, classification),
            "attack_chain": [],
            "potential_harm_description": "",
            "harm_types": [],
        }
        try:
            explanation_data = await self._ai_service.generate_explanation(
                normalized.normalized_text,
                all_signals,
                all_evidence,
                classification,
                rag_context,
            )
        except Exception as e:
            logger.warning(f"Explanation generation failed: {e}")

        # ── 12. Build Scam DNA ────────────────────────────────────────────────
        scam_dna = self._build_scam_dna(all_signals)

        # ── 13. Assemble final response ───────────────────────────────────────
        primary_cat = ScamCategory(classification.get("primary_category", ScamCategory.UNCERTAIN))
        secondary_cats = [
            ScamCategory(c) for c in classification.get("secondary_categories", [])
            if c in ScamCategory.__members__
        ]

        attack_chain = [
            AttackChainStep(step=i + 1, description=step)
            for i, step in enumerate(explanation_data.get("attack_chain", []))
        ]

        potential_harm = None
        if explanation_data.get("potential_harm_description"):
            potential_harm = PotentialHarm(
                description=explanation_data["potential_harm_description"],
                harm_types=explanation_data.get("harm_types", []),
                severity=self._harm_severity(risk.risk_band),
                is_conditional=True,
            )

        processing_ms = int((time.monotonic() - t0) * 1000)

        return FinalAnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            input_modality=normalized.modality,
            language_detected=normalized.language,
            processing_time_ms=processing_ms,
            primary_category=primary_cat,
            secondary_categories=secondary_cats,
            is_likely_scam=classification.get("is_likely_scam", False),
            risk_assessment=risk,
            signals=all_signals,
            evidence=all_evidence,
            attack_chain=attack_chain,
            potential_harm=potential_harm,
            immediate_actions=safety_output["immediate_actions"],
            verification_steps=safety_output["verification_steps"],
            official_contacts=safety_output["official_contacts"],
            incident_response_actions=safety_output["incident_response_actions"],
            explanation=explanation_data["explanation"],
            scam_dna=scam_dna,
            follow_up_questions=safety_output["follow_up_questions"],
            rag_sources_used=rag_sources,
            degraded_mode=degraded_mode,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _merge_signals(
        self,
        rule_signals: list[Signal],
        llm_signals: list[Signal],
        url_signals: list[Signal],
    ) -> list[Signal]:
        """
        Merge signals from all sources. Deduplicate by signal_id.
        When same signal detected by both rule and LLM → mark as hybrid, take max confidence.
        """
        merged: dict[str, Signal] = {}

        for sig in rule_signals + url_signals:
            merged[sig.signal_id] = sig

        for sig in llm_signals:
            if sig.signal_id in merged:
                existing = merged[sig.signal_id]
                # Upgrade to hybrid, take best confidence
                merged[sig.signal_id] = Signal(
                    signal_id=sig.signal_id,
                    category=existing.category,
                    severity=existing.severity,
                    confidence=max(existing.confidence, sig.confidence),
                    detection_source=DetectionSource.HYBRID,
                    false_positive_risk=existing.false_positive_risk,
                )
            else:
                merged[sig.signal_id] = sig

        # Sort by severity then confidence
        severity_order = {SignalSeverity.CRITICAL: 0, SignalSeverity.HIGH: 1, SignalSeverity.MEDIUM: 2, SignalSeverity.LOW: 3}
        return sorted(merged.values(), key=lambda s: (severity_order.get(s.severity, 4), -s.confidence))

    def _should_call_rag(self, classification: dict, risk: RiskAssessment) -> bool:
        return (
            classification.get("primary_category") not in (ScamCategory.UNCERTAIN, "UNCERTAIN")
            and risk.risk_band in (RiskBand.HIGH, RiskBand.CRITICAL)
        )

    def _infer_category_from_signals(self, signals: list[Signal]) -> dict:
        """Fallback category inference from signal categories when LLM classification fails."""
        sig_cats = [s.category for s in signals]
        if "CREDENTIAL_THEFT" in sig_cats:
            return {"primary_category": "KYC", "secondary_categories": [], "confidence": 0.6, "is_likely_scam": True}
        if "REMOTE_ACCESS" in sig_cats:
            return {"primary_category": "REMOTE_ACCESS", "secondary_categories": [], "confidence": 0.8, "is_likely_scam": True}
        if "REWARD" in sig_cats:
            return {"primary_category": "LOTTERY", "secondary_categories": [], "confidence": 0.7, "is_likely_scam": True}
        if "INVESTMENT" in sig_cats:
            return {"primary_category": "INVESTMENT", "secondary_categories": [], "confidence": 0.7, "is_likely_scam": True}
        if signals:
            return {"primary_category": "OTHER", "secondary_categories": [], "confidence": 0.5, "is_likely_scam": True}
        return {"primary_category": "UNCERTAIN", "secondary_categories": [], "confidence": 0.0, "is_likely_scam": False}

    def _build_scam_dna(self, signals: list[Signal]) -> dict[str, float]:
        """Build normalized signal-category strength map for visualization."""
        category_max: dict[str, float] = {}
        severity_map = {SignalSeverity.CRITICAL: 1.0, SignalSeverity.HIGH: 0.75, SignalSeverity.MEDIUM: 0.5, SignalSeverity.LOW: 0.25}
        for sig in signals:
            cat = sig.category.replace("_", " ").title()
            score = severity_map.get(sig.severity, 0.5) * sig.confidence
            category_max[cat] = max(category_max.get(cat, 0.0), score)
        return dict(sorted(category_max.items(), key=lambda x: -x[1]))

    def _default_explanation(self, risk_band: RiskBand, classification: dict) -> str:
        if risk_band in (RiskBand.HIGH, RiskBand.CRITICAL):
            return ("This message contains multiple indicators commonly seen in scam attempts. "
                    "Please do not share any personal information, OTPs, or make any payments. "
                    "Verify independently through official channels.")
        if risk_band == RiskBand.MEDIUM:
            return ("This message contains some suspicious patterns. Exercise caution and verify "
                    "through official channels before taking any action.")
        return ("No strong scam indicators were detected. This does not confirm the message is safe. "
                "When in doubt, verify with the organization through their official contact.")

    def _harm_severity(self, risk_band: RiskBand) -> SignalSeverity:
        return {
            RiskBand.CRITICAL: SignalSeverity.CRITICAL,
            RiskBand.HIGH: SignalSeverity.HIGH,
            RiskBand.MEDIUM: SignalSeverity.MEDIUM,
        }.get(risk_band, SignalSeverity.LOW)
