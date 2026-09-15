"""SCAMX — FastAPI main application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from backend.config import get_settings
from backend.utils.logging_config import setup_logging
from backend.api.analyze import router as analyze_router

# ── Setup ─────────────────────────────────────────────────────────────────────
setup_logging()
settings = get_settings()

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SCAMX",
    description="AI-powered scam detection and safety assistant",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(analyze_router)


@app.get("/api/health", tags=["system"])
async def health_check():
    """Service health check."""
    llm_status = "ok" if settings.gemini_api_key else "not_configured"
    rag_status = "ok"
    try:
        import chromadb  # noqa
    except ImportError:
        rag_status = "not_installed"

    return {
        "status": "ok",
        "version": settings.app_version,
        "env": settings.app_env,
        "llm": llm_status,
        "rag": rag_status,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
