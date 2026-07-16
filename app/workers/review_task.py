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
        # ── Phase 2: Fetch Diff and Post Dummy Comment ───────────────────
        from app.integrations.github_client import GithubClient
        
        client = GithubClient()
        
        # 1. Fetch the raw diff from GitHub
        diff_text = client.get_pr_diff(repo, pr_number)
        
        # 2. Post a dummy comment proving two-way communication works
        dummy_comment = (
            "🤖 **AI Code Review Agent**\n\n"
            "I have successfully received your Pull Request webhook, verified the security signature, "
            f"and fetched the raw diff (`{len(diff_text)} bytes`).\n\n"
            "*(Phase 2 testing complete. AI review generation will be added in Phase 3!)*"
        )
        client.post_pr_comment(repo, pr_number, dummy_comment)

        logger.info(
            "review_task_completed",
            pr_number=pr_number,
            repo=repo,
            status="Phase 2 test complete",
        )

        return {
            "status": "success",
            "pr_number": pr_number,
            "repo": repo,
            "task_id": self.request.id,
            "diff_size": len(diff_text)
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
