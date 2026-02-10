"""Logging configuration helpers."""

from __future__ import annotations

import logging
from typing import Optional


def configure_logging(level: Optional[str] = None) -> None:
    """Configure application logging once.

    Args:
        level: Optional log level name (e.g., "INFO").

    Returns:
        None.
    """

    if logging.getLogger().handlers:
        return

    resolved = None
    if level:
        resolved = getattr(logging, level.upper(), None)
    logging.basicConfig(level=resolved or logging.INFO)
