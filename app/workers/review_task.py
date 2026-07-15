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
        # ── Phase 1 placeholder ───────────────────────────────────────────
        # Real logic will replace this in Phase 2 & 3
        logger.info(
            "review_task_completed",
            pr_number=pr_number,
            repo=repo,
            status="placeholder — agents not yet built",
        )

        return {
            "status": "queued",
            "pr_number": pr_number,
            "repo": repo,
            "task_id": self.request.id,
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
