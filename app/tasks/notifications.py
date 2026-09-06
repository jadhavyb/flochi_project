from __future__ import annotations

import logging

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.process_notification")
def process_notification(user_id: str, message: str) -> dict:
    logger.info("Processing notification for user %s: %s", user_id, message)
    return {"status": "processed", "user_id": user_id}
