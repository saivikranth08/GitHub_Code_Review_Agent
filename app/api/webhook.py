from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
import structlog
from typing import Optional
from app.config import settings
from app.workers.review_task import run_review

logger = structlog.get_logger()
router = APIRouter()

async def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verifies the HMAC signature of the webhook payload using the secret from .env.
    """
    if not signature_header:
        return False
        
    hash_object = hmac.new(
        settings.github_webhook_secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """
    Webhook receiver for GitHub events.
    Verifies the signature, parses the payload, and dispatches to Celery.
    """
    # 1. Read the raw payload for signature verification
    payload_body = await request.body()
    
    # 2. Verify Security Signature
    if not await verify_github_signature(payload_body, x_hub_signature_256):
        logger.warning("webhook_signature_failed")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Parse JSON payload
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 4. Handle only Pull Request events
    if x_github_event == "ping":
        logger.info("webhook_ping_received")
        return {"status": "pong"}
        
    if x_github_event != "pull_request":
        logger.info("webhook_ignored_event", event=x_github_event)
        return {"status": "ignored", "reason": "not a pull_request event"}
        
    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        logger.info("webhook_ignored_action", action=action)
        return {"status": "ignored", "reason": f"action {action} not handled"}

    # 5. Extract PR Metadata
    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})
    
    pr_number = pr_data.get("number")
    repo_full_name = repo_data.get("full_name")
    pr_title = pr_data.get("title", "")
    author = pr_data.get("user", {}).get("login", "")

    if not pr_number or not repo_full_name:
        logger.error("webhook_missing_data", payload=payload)
        raise HTTPException(status_code=400, detail="Missing PR number or repository info")

    # 6. Dispatch to Celery (Background Worker)
    logger.info("webhook_dispatching_review", pr=pr_number, repo=repo_full_name)
    
    task = run_review.delay(
        pr_number=pr_number,
        repo=repo_full_name,
        pr_title=pr_title,
        author=author
    )

    # 7. Immediately return 202 Accepted to GitHub (< 1 second)
    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "message": "Review queued successfully",
            "task_id": task.id
        }
    )
