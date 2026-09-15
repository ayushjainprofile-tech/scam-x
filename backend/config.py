"""
SCAMX — Application Configuration
All settings are loaded from environment variables via .env file.
Never hardcode secrets or API keys.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # === Application ===
    app_env: str = "development"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # === LLM — Gemini ===
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-1.5-flash"
    gemini_pro_model: str = "gemini-1.5-pro"
    llm_flash_timeout: int = 10   # seconds
    llm_pro_timeout: int = 15
    llm_max_retries: int = 3

    # === Speech-to-Text — OpenAI Whisper ===
    openai_api_key: str = ""

    # === RAG — ChromaDB ===
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "scamx_knowledge"

    # === Input limits ===
    max_text_length: int = 5000
    max_image_size_mb: int = 10
    max_audio_duration_seconds: int = 180  # 3 minutes
    max_audio_size_mb: int = 25

    # === Rate limiting ===
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60

    # === CORS ===
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
