"""
Global constants used across NetScope.

This module intentionally contains only immutable values.
"""

from __future__ import annotations

from pathlib import Path

PACKAGE_NAME: str = "netscope"

DEFAULT_LOGGER_NAME: str = PACKAGE_NAME

DEFAULT_REPORT_DIRECTORY: str = "reports"

DEFAULT_ARTIFACT_DIRECTORY: str = "artifacts"

DEFAULT_SNAPSHOT_DIRECTORY: str = "snapshots"

DEFAULT_ENCODING: str = "utf-8"

DEFAULT_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

PROJECT_ROOT: Path = Path.cwd()

SUPPORTED_DEVICES: tuple[str, ...] = (
    "cpu",
    "cuda",
    "mps",
)

SUPPORTED_EXPORT_FORMATS: tuple[str, ...] = (
    "json",
    "html",
    "npz",
)

SUPPORTED_PRECISIONS: tuple[str, ...] = (
    "float32",
    "float16",
    "bfloat16",
)

__all__ = [
    "PACKAGE_NAME",
    "DEFAULT_LOGGER_NAME",
    "DEFAULT_REPORT_DIRECTORY",
    "DEFAULT_ARTIFACT_DIRECTORY",
    "DEFAULT_SNAPSHOT_DIRECTORY",
    "DEFAULT_ENCODING",
    "DEFAULT_DATETIME_FORMAT",
    "PROJECT_ROOT",
    "SUPPORTED_DEVICES",
    "SUPPORTED_EXPORT_FORMATS",
    "SUPPORTED_PRECISIONS",
]