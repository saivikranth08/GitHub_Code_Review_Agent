# Main Celery task — orchestrates full review pipeline
# Phase 1: Placeholder — logs the job, returns status
# Phase 2: Will add GitHub diff fetching + sanitization
# Phase 3: Will add LangGraph agent orchestration

from app.workers.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(
    bind=True,            # gives access to self (for retries)
    max_retries=3,
    default_retry_delay=60,
    name="app.workers.review_task.run_review"
)
def run_review(
    self,
    pr_number: int,
    repo: str,
    pr_title: str = "",
    author: str = "",
):
    """
    Main review task. Called via run_review.delay() from the webhook handler.

    Flow (grows with each phase):
    Phase 1: Log job received
    Phase 2: Fetch diff from GitHub → sanitize → store in DB
    Phase 3: Run 6 agents in parallel via LangGraph → post findings to PR
    Phase 4: Store patterns in Qdrant → update learning system
    Phase 5: Run RAGAS quality measurement
    """
    logger.info(
        "review_task_started",
        pr_number=pr_number,
        repo=repo,
        pr_title=pr_title,
        author=author,
        task_id=self.request.id,
    )

    try:
        # ── Phase 3: LangGraph Orchestration ────────────────────────────
        from app.integrations.github_client import GithubClient
        from app.orchestrator.graph import review_graph
        
        client = GithubClient()
        
        # 1. Fetch the raw diff from GitHub
        diff_text = client.get_pr_diff(repo, pr_number)
        
        # 2. Skip if diff is empty
        if not diff_text.strip():
            client.post_pr_comment(repo, pr_number, "🤖 **AI Code Review Agent**\n\nNo code changes found to review.")
            return {"status": "success", "findings": 0}

        # 3. Execute the LangGraph Orchestrator
        logger.info("executing_langgraph", pr_number=pr_number)
        
        initial_state = {
            "pr_number": pr_number,
            "repo": repo,
            "diff_text": diff_text,
            "findings": []
        }
        
        # Run the graph
        final_state = review_graph.invoke(initial_state)
        all_findings = final_state.get("findings", [])
        
        # 3.5. Quality Evaluation (LLM-as-a-judge)
        if all_findings:
            from app.core.quality import QualityEvaluator
            from app.config import settings
            evaluator = QualityEvaluator()
            
            high_quality_findings = []
            for finding in all_findings:
                score = evaluator.evaluate_finding(diff_text, finding)
                if score.confidence_score >= settings.confidence_threshold:
                    high_quality_findings.append(finding)
                else:
                    logger.warning("finding_rejected_by_judge", title=finding.title, score=score.confidence_score, reason=score.reason)
            
            all_findings = high_quality_findings

        # 4. Format findings into a beautiful Markdown comment
        if not all_findings:
            comment_body = "🤖 **AI Code Review Agent**\n\n✅ Great job! All 3 AI agents (Security, Performance, Style) reviewed the code and found zero issues."
        else:
            comment_body = f"🤖 **AI Code Review Agent**\n\n⚠️ Found **{len(all_findings)}** potential issues across 3 agents.\n\n"
            
            # Build Summary Table
            comment_body += "### 📊 Summary\n"
            comment_body += "| Severity | Category | File | Line | Issue |\n"
            comment_body += "|----------|----------|------|------|-------|\n"
            
            for f in all_findings:
                sev_icon = "🔴" if f.severity == "HIGH" else "🟠" if f.severity == "MEDIUM" else "🟡"
                comment_body += f"| {sev_icon} {f.severity} | {f.category} | `{f.file_path}` | {f.line_number} | {f.title} |\n"
            
            # Build Detailed Findings
            comment_body += "\n---\n\n### 🔍 Detailed Findings\n\n"
            for f in all_findings:
                sev_icon = "🔴" if f.severity == "HIGH" else "🟠" if f.severity == "MEDIUM" else "🟡"
                comment_body += f"#### {sev_icon} {f.severity}: {f.title} ({f.category})\n"
                comment_body += f"**Location:** `{f.file_path}` (Line {f.line_number})\n\n"
                comment_body += f"{f.description}\n\n"
                comment_body += "**Suggested Fix:**\n"
                if f.suggestion.startswith("```"):
                    comment_body += f"{f.suggestion}\n\n"
                else:
                    comment_body += f"```python\n{f.suggestion}\n```\n\n"

        # 5. Post to GitHub
        client.post_pr_comment(repo, pr_number, comment_body)
        
        # 6. Save findings to Qdrant for Long-Term Memory
        if all_findings:
            from app.memory.qdrant_store import QdrantStore
            qdrant = QdrantStore()
            for finding in all_findings:
                qdrant.save_finding(pr_number, repo, finding)

        logger.info(
            "review_task_completed",
            pr_number=pr_number,
            repo=repo,
            findings_count=len(all_findings),
            status="Phase 3 review complete",
        )

        return {
            "status": "success",
            "pr_number": pr_number,
            "repo": repo,
            "task_id": self.request.id,
            "findings_count": len(all_findings)
        }

    except Exception as exc:
        logger.error(
            "review_task_failed",
            pr_number=pr_number,
            repo=repo,
            error=str(exc),
            retries_left=self.max_retries - self.request.retries,
        )
        # Retry after 60 seconds, up to 3 times
        raise self.retry(exc=exc)
