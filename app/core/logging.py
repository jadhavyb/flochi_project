from __future__ import annotations

import logging
import sys

from app.core.config import settings


class HealthFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().startswith("GET /health")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    logging.getLogger("uvicorn.access").addFilter(HealthFilter())
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
