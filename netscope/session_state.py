"""
Session lifecycle states.

This module models the higher-level session state used by the execution layer.
It is distinct from the low-level component lifecycle state.
"""

from __future__ import annotations

from enum import Enum


class SessionState(str, Enum):
    """High-level session states."""

    CREATED = "created"
    PREPARED = "prepared"
    RUNNING = "running"
    STOPPED = "stopped"
    CLOSED = "closed"
    FAILED = "failed"


__all__ = [
    "SessionState",
]