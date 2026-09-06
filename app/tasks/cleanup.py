from __future__ import annotations

import logging

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.cleanup_expired_sessions")
def cleanup_expired_sessions() -> dict:
    logger.info("Running expired session cleanup")
    return {"status": "completed"}
