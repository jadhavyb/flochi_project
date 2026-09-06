from __future__ import annotations

import logging

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.send_welcome_email")
def send_welcome_email(user_email: str, first_name: str | None = None) -> dict:
    logger.info("Sending welcome email to %s", user_email)
    return {"status": "sent", "email": user_email}
