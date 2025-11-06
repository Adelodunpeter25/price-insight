"""Logging configuration."""

import logging
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """Setup application logging."""
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def log_event(event: str, data: Dict[str, Any] = None) -> None:
    """Log structured event."""
    logger = logging.getLogger(__name__)
    logger.info(f"EVENT: {event} {data or ''}")