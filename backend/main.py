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


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

# ── Mount Frontend Static Assets ─────────────────────────────────────────────
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
