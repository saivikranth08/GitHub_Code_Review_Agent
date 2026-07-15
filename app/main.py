# FastAPI application entry point
# Runs inside the 'api' Docker container on port 8000
# Nginx routes external traffic here

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

import asyncpg
import redis.asyncio as aioredis
from qdrant_client import QdrantClient

from app.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    Startup: log that the app is ready.
    Shutdown: clean up connections.
    """
    logger.info(
        "api_starting",
        env=settings.app_env,
        version="1.0.0"
    )
    yield
    logger.info("api_shutting_down")


app = FastAPI(
    title="AI Code Review Pipeline",
    description="6 parallel AI agents reviewing GitHub Pull Requests instantly",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",      # Swagger UI at /api/docs
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Docker uses this to know when the api container is ready.
    Also used by Nginx and other services that depend on api.

    Returns status of all 3 infrastructure services:
    - postgres: primary database
    - redis: task queue + cache
    - qdrant: vector store
    """
    health = {
        "status": "ok",
        "env": settings.app_env,
        "services": {}
    }

    # ── Check PostgreSQL ───────────────────────────────────────────────────
    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
        )
        await conn.execute("SELECT 1")
        await conn.close()
        health["services"]["postgres"] = "up"
    except Exception as e:
        logger.warning("postgres_health_failed", error=str(e))
        health["services"]["postgres"] = "down"
        health["status"] = "degraded"

    # ── Check Redis ────────────────────────────────────────────────────────
    try:
        r = aioredis.from_url(settings.celery_broker_url)
        await r.ping()
        await r.aclose()
        health["services"]["redis"] = "up"
    except Exception as e:
        logger.warning("redis_health_failed", error=str(e))
        health["services"]["redis"] = "down"
        health["status"] = "degraded"

    # ── Check Qdrant ───────────────────────────────────────────────────────
    try:
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=5
        )
        client.get_collections()
        health["services"]["qdrant"] = "up"
    except Exception as e:
        logger.warning("qdrant_health_failed", error=str(e))
        health["services"]["qdrant"] = "down"
        health["status"] = "degraded"

    logger.info("health_check", **health)
    return health


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "AI Code Review Pipeline",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# ── Register routers (added phase by phase) ───────────────────────────────────
# Phase 2: from app.api.webhook import router as webhook_router
# Phase 2: app.include_router(webhook_router)
# Phase 3: from app.api.dashboard import router as dashboard_router
# Phase 5: from app.api.feedback import router as feedback_router
