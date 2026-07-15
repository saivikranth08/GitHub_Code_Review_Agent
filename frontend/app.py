# Streamlit dashboard entry point — Phase 1 skeleton
# Full dashboard built in Phase 6

import streamlit as st
import httpx
from app.config import settings

st.set_page_config(
    page_title="AI Code Review Pipeline",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.title("🤖 Code Review Pipeline")
st.sidebar.caption("AI-powered parallel code reviews")
st.sidebar.divider()
st.sidebar.markdown("**Phases**")
st.sidebar.markdown("✅ Phase 1 — Infrastructure")
st.sidebar.markdown("⏳ Phase 2 — GitHub Integration")
st.sidebar.markdown("⏳ Phase 3 — Agents")
st.sidebar.markdown("⏳ Phase 4 — Memory")
st.sidebar.markdown("⏳ Phase 5 — Quality")
st.sidebar.markdown("⏳ Phase 6 — Dashboard")

# ── Main ───────────────────────────────────────────────────────────────────
st.title("🤖 AI Code Review Pipeline")
st.caption("6 parallel AI agents reviewing your GitHub Pull Requests instantly")

st.divider()

# Live system health check
st.subheader("⚙️ System Status")

try:
    response = httpx.get("http://api:8000/health", timeout=5)
    health = response.json()

    col1, col2, col3, col4 = st.columns(4)

    overall = health.get("status", "unknown")
    col1.metric("Overall", "🟢 OK" if overall == "ok" else "🔴 Degraded")

    services = health.get("services", {})
    col2.metric("PostgreSQL", "🟢 Up" if services.get("postgres") == "up" else "🔴 Down")
    col3.metric("Redis", "🟢 Up" if services.get("redis") == "up" else "🔴 Down")
    col4.metric("Qdrant", "🟢 Up" if services.get("qdrant") == "up" else "🔴 Down")

except Exception as e:
    st.error(f"Cannot reach API: {e}")

st.divider()
st.info("📊 Full dashboard with review metrics, cost tracking, and quality trends will be built in Phase 6.")
