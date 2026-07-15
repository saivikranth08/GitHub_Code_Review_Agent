# Celery app configuration and broker setup
# This file is imported by BOTH:
#   - api container (to call .delay() and enqueue jobs)
#   - worker container (to run the actual tasks)

from celery import Celery
from app.config import settings


celery_app = Celery(
    "code_review",                              # app name
    broker=settings.celery_broker_url,          # redis db 0 — job queue
    backend=settings.celery_result_backend,     # redis db 1 — job results
    include=["app.workers.review_task"]         # where tasks are defined
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task behavior
    task_track_started=True,     # shows "STARTED" state in Flower UI
    task_acks_late=True,         # only mark job done AFTER it finishes (safe retry)
    worker_prefetch_multiplier=1, # worker takes 1 job at a time (fair for long tasks)

    # Result expiry — keep job results in Redis for 24 hours
    result_expires=86400,

    # Named queues — reviews go to 'reviews' queue
    task_routes={
        "app.workers.review_task.run_review": {"queue": "reviews"},
    },

    # Retry settings
    task_default_retry_delay=60,   # wait 60 seconds before retry
    task_max_retries=3,            # retry up to 3 times on failure
)
