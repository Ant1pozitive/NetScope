"""
Common enumerations used across NetScope.
"""

from __future__ import annotations

from enum import Enum


class DeviceType(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class ExecutionMode(str, Enum):
    TRAIN = "train"
    EVAL = "eval"
    INFERENCE = "inference"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


__all__ = [
    "DeviceType",
    "ExecutionMode",
    "LogLevel",
]