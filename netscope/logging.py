"""
Logging subsystem.
"""

from __future__ import annotations

import logging

from .config import CONFIG
from .constants import DEFAULT_LOGGER_NAME

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(
    name: str = DEFAULT_LOGGER_NAME,
) -> logging.Logger:
    """
    Return configured logger.

    Logger instances are cached.
    """

    if name in _LOGGERS:
        return _LOGGERS[name]

    config = CONFIG.config.logging

    logger = logging.getLogger(name)

    logger.setLevel(config.level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s :: %(message)s"
    )

    if config.enable_console:

        console = logging.StreamHandler()

        console.setFormatter(formatter)

        logger.addHandler(console)

    if config.enable_file:

        file_handler = logging.FileHandler(
            config.filename,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    logger.propagate = False

    _LOGGERS[name] = logger

    return logger