# Initialize PostgreSQL schema on first startup
# Run with: docker compose exec api python scripts/init_db.py

import asyncio
import asyncpg
from app.config import settings

# ── SQL Schema ────────────────────────────────────────────────────────────────

CREATE_TABLES = """

-- Stores every PR review session
CREATE TABLE IF NOT EXISTS reviews (
    id              SERIAL PRIMARY KEY,
    repo            VARCHAR(255)    NOT NULL,
    pr_number       INTEGER         NOT NULL,
    pr_title        TEXT,
    author          VARCHAR(255),
    diff_hash       VARCHAR(64),
    status          VARCHAR(20)     DEFAULT 'pending',  -- pending|running|done|failed
    total_findings  INTEGER         DEFAULT 0,
    critical_count  INTEGER         DEFAULT 0,
    high_count      INTEGER         DEFAULT 0,
    medium_count    INTEGER         DEFAULT 0,
    low_count       INTEGER         DEFAULT 0,
    total_cost_usd  DECIMAL(10,6)   DEFAULT 0,
    duration_ms     INTEGER,
    created_at      TIMESTAMP       DEFAULT NOW(),
    completed_at    TIMESTAMP
);

-- Stores individual findings from each agent
CREATE TABLE IF NOT EXISTS findings (
    id               SERIAL PRIMARY KEY,
    review_id        INTEGER         REFERENCES reviews(id) ON DELETE CASCADE,
    agent_type       VARCHAR(50)     NOT NULL,     -- security|performance|style|...
    severity         VARCHAR(20)     NOT NULL,     -- critical|high|medium|low|info
    file_path        TEXT,
    line_number      INTEGER,
    title            TEXT            NOT NULL,
    description      TEXT,
    suggestion       TEXT,
    confidence_score DECIMAL(4,3),                -- 0.000 to 1.000
    model_used       VARCHAR(100),                -- which LLM produced this
    cost_usd         DECIMAL(10,6)   DEFAULT 0,
    is_valid         BOOLEAN,                     -- null=unreviewed, true, false
    pattern_type     VARCHAR(100),                -- sql_injection|n_plus_one|...
    created_at       TIMESTAMP       DEFAULT NOW()
);

-- Stores embeddings metadata for Qdrant-stored patterns
CREATE TABLE IF NOT EXISTS code_patterns (
    id               SERIAL PRIMARY KEY,
    pattern_type     VARCHAR(100)    NOT NULL,
    language         VARCHAR(50),
    description      TEXT,
    qdrant_point_id  VARCHAR(64),
    example_code     TEXT,
    fix_suggestion   TEXT,
    occurrence_count INTEGER         DEFAULT 1,
    created_at       TIMESTAMP       DEFAULT NOW()
);

-- Stores developer feedback on findings (valid/invalid/duplicate)
CREATE TABLE IF NOT EXISTS feedback (
    id                   SERIAL PRIMARY KEY,
    finding_id           INTEGER     REFERENCES findings(id) ON DELETE CASCADE,
    developer_github_id  VARCHAR(255),
    feedback_type        VARCHAR(20) NOT NULL,  -- valid|invalid|duplicate
    comment              TEXT,
    created_at           TIMESTAMP   DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_reviews_repo        ON reviews(repo);
CREATE INDEX IF NOT EXISTS idx_reviews_repo_pr     ON reviews(repo, pr_number);
CREATE INDEX IF NOT EXISTS idx_reviews_status      ON reviews(status);
CREATE INDEX IF NOT EXISTS idx_findings_review     ON findings(review_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity   ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_agent      ON findings(agent_type);
CREATE INDEX IF NOT EXISTS idx_findings_valid      ON findings(is_valid);
"""

# ── Runner ────────────────────────────────────────────────────────────────────

async def init_db():
    print("🔌 Connecting to PostgreSQL...")
    conn = await asyncpg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )
    print("📦 Creating tables and indexes...")
    await conn.execute(CREATE_TABLES)
    await conn.close()
    print("✅ PostgreSQL schema initialized successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
