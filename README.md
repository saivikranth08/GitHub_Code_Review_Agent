# AI-Powered Code Review Pipeline 

> **6 specialized AI agents that review your GitHub Pull Requests in parallel — instantly, consistently, and at a fraction of the cost.**

---

## What This Does

When a developer pushes code to GitHub, 6 AI agents wake up simultaneously — each an expert in their domain:

| Agent | Speciality |
|---|---|
| 🔐 Security Agent | SQL injection, exposed credentials, auth bypass |
| ⚡ Performance Agent | N+1 queries, memory leaks, inefficient algorithms |
| 🎨 Style Agent | Naming conventions, formatting, code style |
| 🏗️ Architecture Agent | SOLID violations, bad design patterns |
| 🧪 Test Agent | Missing coverage, untested edge cases |
| 📋 Compliance Agent | GDPR violations, PII exposure |

They finish in seconds. Not days.

---

## Architecture

```
GitHub PR → Webhook → Sanitize → Router → 6 Parallel Agents
                                                ↓
                           Merge & Deduplicate Findings
                                                ↓
                           Quality Measurement (RAGAS)
                                                ↓
                           Post PR Comments → Learn & Improve
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI + Python 3.11 |
| **Task Queue** | Celery + Redis |
| **Orchestration** | LangGraph |
| **LLMs** | GPT-4o (Groq) · Claude Sonnet · Llama 3.3 (Groq free) |
| **Vector DB** | Qdrant |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Embeddings** | Sentence Transformers (local) |
| **Evaluation** | RAGAS |
| **Tracing** | LangSmith |
| **Frontend** | Streamlit |
| **Proxy** | Nginx |
| **Containers** | Docker + Docker Compose |
| **Monitoring** | Prometheus + Grafana |

---

## Project Phases

- **Phase 1** — Foundation & Docker (all infrastructure running)
- **Phase 2** — GitHub Integration & Sanitization
- **Phase 3** — LangGraph Orchestration & 6 Agents
- **Phase 4** — Memory & Learning System
- **Phase 5** — Quality Measurement & Feedback Loop
- **Phase 6** — Dashboard & Monitoring

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/saivikranth08/GitHub_Code_Review_Agent.git
cd GitHub_Code_Review_Agent

# Copy environment variables
cp .env.example .env
# Fill in your API keys in .env

# Start everything
docker compose up -d

# Check all services are healthy
docker compose ps
```

Open `http://localhost` to access the dashboard.

---

## Environment Variables

See [.env.example](.env.example) for all required configuration.

---

## Project Structure

```
├── docker/               # Dockerfiles & service configs
├── app/                  # FastAPI application
│   ├── api/              # Webhook & REST endpoints
│   ├── agents/           # 6 AI review agents
│   ├── core/             # Sanitizer, router, merger, quality
│   ├── orchestrator/     # LangGraph graph & state
│   ├── memory/           # Qdrant, PostgreSQL, Redis clients
│   ├── workers/          # Celery tasks
│   └── integrations/     # GitHub API, LLM factory, LangSmith
├── frontend/             # Streamlit dashboard
├── prompts/              # Agent system prompts
├── scripts/              # DB init, Qdrant setup, seeding
└── tests/                # Unit & integration tests
```

---

## Cost

~$0.10–0.16 per review (3x cheaper than GPT-4 only approaches)

- Complex agents (Security, Architecture) → GPT-4o via Groq
- Balanced agents (Performance, Testing) → Claude Sonnet
- Fast agents (Style, Compliance) → Llama 3.3 via Groq (free)

---

*Built with LangGraph · LangChain · FastAPI · Docker*
