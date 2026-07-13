"""
Graph direction definitions.
"""

from __future__ import annotations

from enum import Enum


class GraphDirection(str, Enum):
    """Edge direction for graph primitives."""

    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"
    UNDIRECTED = "undirected"


__all__ = [
    "GraphDirection",
]