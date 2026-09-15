"""
SCAMX — Analysis API Endpoints
POST /api/analyze/text
POST /api/analyze/image
POST /api/analyze/audio
POST /api/analyze/url
POST /api/feedback
"""

import json
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from loguru import logger
from backend.schemas.input import TextAnalysisRequest, URLAnalysisRequest, SessionContext
from backend.schemas.response import FinalAnalysisResponse, FeedbackRequest
from backend.core.orchestrator import AnalysisOrchestrator
from backend.config import get_settings

router = APIRouter(prefix="/api", tags=["analysis"])
_orchestrator = AnalysisOrchestrator()
_settings = get_settings()

# ── Supported MIME types ──────────────────────────────────────────────────────
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
SUPPORTED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg", "audio/m4a"}


@router.post("/analyze/text", response_model=FinalAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze suspicious text content (SMS, WhatsApp message, email, etc.)
    """
    try:
        result = await _orchestrator.analyze_text(
            text=request.text,
            language_hint=request.language_hint,
            session_context=request.session_context,
        )
        return result
    except Exception as e:
        logger.error(f"Text analysis error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.post("/analyze/image", response_model=FinalAnalysisResponse)
async def analyze_image(
    image: UploadFile = File(..., description="Screenshot to analyze (JPG/PNG/WebP)"),
    session_context: str = Form(None, description="JSON-encoded SessionContext"),
):
    """
    Analyze a screenshot. OCR extracts text, then runs full scam analysis.
    """
    # Validate MIME type
    if image.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type. Supported: JPEG, PNG, WebP"
        )

    # Validate file size
    image_bytes = await image.read()
    max_bytes = _settings.max_image_size_mb * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large. Maximum size: {_settings.max_image_size_mb}MB"
        )

    # Parse session context if provided
    ctx = None
    if session_context:
        try:
            ctx = SessionContext(**json.loads(session_context))
        except Exception:
            pass  # Invalid context is not fatal

    try:
        result = await _orchestrator.analyze_image(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            session_context=ctx,
        )

        # Handle empty OCR
        if not result.signals and result.risk_assessment.risk_band.value == "UNCERTAIN":
            if result.explanation == "" or "No strong" in result.explanation:
                raise HTTPException(
                    status_code=422,
                    detail="Could not extract readable text from this image. Please try a clearer photo or paste the text directly."
                )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Image analysis failed. Please try again.")


@router.post("/analyze/audio", response_model=FinalAnalysisResponse)
async def analyze_audio(
    audio: UploadFile = File(..., description="Voice note to analyze"),
    session_context: str = Form(None),
):
    """
    Transcribe voice note with Whisper, then run full scam analysis on transcript.
    Analysis is based on transcribed text only — no speaker or emotion detection.
    """
    if audio.content_type not in SUPPORTED_AUDIO_TYPES and not audio.filename.lower().endswith((".mp3", ".wav", ".m4a", ".ogg")):
        raise HTTPException(status_code=400, detail="Unsupported audio format. Use MP3, WAV, M4A, or OGG.")

    audio_bytes = await audio.read()
    max_audio_bytes = _settings.max_audio_size_mb * 1024 * 1024
    if len(audio_bytes) > max_audio_bytes:
        raise HTTPException(status_code=400, detail=f"Audio too large. Maximum: {_settings.max_audio_size_mb}MB")

    ctx = None
    if session_context:
        try:
            ctx = SessionContext(**json.loads(session_context))
        except Exception:
            pass

    try:
        result = await _orchestrator.analyze_audio(
            audio_bytes=audio_bytes,
            filename=audio.filename or "audio.mp3",
            session_context=ctx,
        )
        return result
    except Exception as e:
        logger.error(f"Audio analysis error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Audio analysis failed. Please try again.")


@router.post("/analyze/url", response_model=FinalAnalysisResponse)
async def analyze_url(request: URLAnalysisRequest):
    """
    Static analysis of a suspicious URL. No HTTP requests made to the target URL.
    """
    # Block private IP ranges explicitly
    import re
    from backend.utils.constants import PRIVATE_IP_PATTERNS
    for pat in PRIVATE_IP_PATTERNS:
        if re.search(pat, request.url):
            raise HTTPException(status_code=422, detail="Private or local IP addresses cannot be analyzed.")

    try:
        result = await _orchestrator.analyze_url(
            url=request.url,
            session_context=request.session_context,
        )
        return result
    except Exception as e:
        logger.error(f"URL analysis error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="URL analysis failed. Please try again.")


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Collect user feedback on analysis quality.
    Feedback is logged only — no automatic model retraining.
    """
    # Log for human review only — no user content stored
    logger.info(
        f"Feedback received: analysis_id={request.analysis_id} "
        f"was_scam={request.was_scam} helpful={request.recommendation_helpful}"
    )
    return {"received": True}
