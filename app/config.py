# Pydantic settings — loads all config from .env
# Every service in the app imports settings from here
# Usage: from app.config import settings

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # ── GitHub ────────────────────────────────────────────────────────────────
    github_webhook_secret: str = ""
    github_token: str = ""

    # ── LLM (Groq only) ───────────────────────────────────────────────────────
    groq_api_key: str = ""

    # ── LangSmith ─────────────────────────────────────────────────────────────
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "code-review-pipeline"

    # ── PostgreSQL ─────────────────────────────────────────────────────────────
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "code_review"
    postgres_user: str = "review_user"
    postgres_password: str = ""
    database_url: str = "postgresql+asyncpg://review_user:password@postgres:5432/code_review"

    # ── Redis ──────────────────────────────────────────────────────────────────
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_url: str = "redis://redis:6379/2"           # db 2 = app cache
    celery_broker_url: str = "redis://redis:6379/0"   # db 0 = job queue
    celery_result_backend: str = "redis://redis:6379/1" # db 1 = job results

    # ── Qdrant ────────────────────────────────────────────────────────────────
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "code_patterns"

    # ── Application ───────────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "INFO"
    api_port: int = 8000

    # ── Agent Config ──────────────────────────────────────────────────────────
    confidence_threshold: float = 0.75   # findings below this are not posted
    max_diff_tokens: int = 8000          # chunk diffs larger than this
    daily_cost_cap_usd: float = 5.00     # per-repo daily spending limit

    # ── Monitoring ────────────────────────────────────────────────────────────
    grafana_password: str = "admin"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"   # ignore unknown .env keys


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    lru_cache means Settings() is only created once — not on every import.
    """
    return Settings()


# Single shared instance used across the whole app
settings = get_settings()
