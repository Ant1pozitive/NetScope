"""
Hook kind definitions.
"""

from __future__ import annotations

from enum import Enum


class HookKind(str, Enum):
    """Supported hook kinds."""

    FORWARD = "forward"
    BACKWARD = "backward"
    PRE_FORWARD = "pre_forward"
    POST_FORWARD = "post_forward"
    CUSTOM = "custom"


__all__ = [
    "HookKind",
]