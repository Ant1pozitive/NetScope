"""
Logging utilities.
"""

from __future__ import annotations

import logging

from .config import DEFAULT_CONFIG
from .constants import DEFAULT_LOGGER_NAME


def get_logger(name: str = DEFAULT_LOGGER_NAME) -> logging.Logger:
    """
    Return configured logger instance.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(DEFAULT_CONFIG.logging.level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
    )

    if DEFAULT_CONFIG.logging.enable_console:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if DEFAULT_CONFIG.logging.enable_file:
        handler = logging.FileHandler(
            DEFAULT_CONFIG.logging.filename,
            encoding="utf-8",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False

    return logger


__all__ = [
    "get_logger",
]