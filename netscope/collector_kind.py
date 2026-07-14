"""
Collector kind definitions.
"""

from __future__ import annotations

from enum import Enum


class CollectorKind(str, Enum):
    """Supported collector kinds."""

    ACTIVATION = "activation"
    GRADIENT = "gradient"
    WEIGHT = "weight"
    RUNTIME = "runtime"
    CUSTOM = "custom"


__all__ = [
    "CollectorKind",
]