"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).with_name(".env"))


class Settings(BaseModel):
    app_name: str = "Shop with Confidence API"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    # Gemini
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.5-flash-lite", alias="GEMINI_MODEL")
    gemini_fallback_model: str = Field(
        default="gemini-3.6-flash", alias="GEMINI_FALLBACK_MODEL"
    )
    gemini_timeout_ms: int = Field(default=20_000, alias="GEMINI_TIMEOUT_MS")
    gemini_retry_attempts: int = Field(default=2, alias="GEMINI_RETRY_ATTEMPTS")

    # Perfect Corp / YouCam
    youcam_api_key: str | None = Field(default=None, alias="YOUCAM_API_KEY")
    youcam_api_base_url: str | None = Field(
        default=None,
        alias="YOUCAM_API_BASE_URL",
    )
    youcam_skin_analysis_url: str | None = Field(
        default=None,
        alias="YOUCAM_SKIN_ANALYSIS_URL",
    )
    youcam_clothes_tryon_url: str | None = Field(
        default=None,
        alias="YOUCAM_CLOTHES_TRYON_URL",
    )
    youcam_auth_header: str = Field(
        default="X-API-KEY",
        alias="YOUCAM_AUTH_HEADER",
    )
    youcam_auth_prefix: str = Field(
        default="",
        alias="YOUCAM_AUTH_PREFIX",
    )

    # Application mode
    ai_mode: str = Field(default="mock", alias="AI_MODE")

    # HTTP
    request_timeout_seconds: float = Field(
        default=20.0,
        alias="REQUEST_TIMEOUT_SECONDS",
    )

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = {"populate_by_name": True}


@lru_cache
def get_settings() -> Settings:
    return Settings(
        APP_ENV=os.getenv("APP_ENV", "development"),
        DEBUG=os.getenv("DEBUG", "true"),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
        GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        GEMINI_FALLBACK_MODEL=os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.6-flash"),
        GEMINI_TIMEOUT_MS=os.getenv("GEMINI_TIMEOUT_MS", "20000"),
        GEMINI_RETRY_ATTEMPTS=os.getenv("GEMINI_RETRY_ATTEMPTS", "2"),
        YOUCAM_API_KEY=os.getenv("YOUCAM_API_KEY"),
        YOUCAM_API_BASE_URL=os.getenv("YOUCAM_API_BASE_URL"),
        YOUCAM_SKIN_ANALYSIS_URL=os.getenv("YOUCAM_SKIN_ANALYSIS_URL"),
        YOUCAM_CLOTHES_TRYON_URL=os.getenv("YOUCAM_CLOTHES_TRYON_URL"),
        YOUCAM_AUTH_HEADER=os.getenv("YOUCAM_AUTH_HEADER", "X-API-KEY"),
        YOUCAM_AUTH_PREFIX=os.getenv("YOUCAM_AUTH_PREFIX", ""),
        AI_MODE=os.getenv("AI_MODE", "mock"),
        REQUEST_TIMEOUT_SECONDS=os.getenv("REQUEST_TIMEOUT_SECONDS", "20"),
        allowed_origins=[
            origin.strip()
            for origin in os.getenv(
                "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ],
    )
