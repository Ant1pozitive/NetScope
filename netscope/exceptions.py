"""
NetScope exception hierarchy.
"""

from __future__ import annotations


class NetScopeError(Exception):
    """Base exception for all NetScope errors."""


class ConfigurationError(NetScopeError):
    """Raised when configuration is invalid."""


class SnapshotError(NetScopeError):
    """Raised during snapshot generation."""


class HookError(NetScopeError):
    """Raised by hook manager."""


class CollectorError(NetScopeError):
    """Raised by collectors."""


class AnalyzerError(NetScopeError):
    """Raised by analyzers."""


class SerializationError(NetScopeError):
    """Raised during serialization."""


class UnsupportedModelError(NetScopeError):
    """Raised when model type is unsupported."""


__all__ = [
    "NetScopeError",
    "ConfigurationError",
    "SnapshotError",
    "HookError",
    "CollectorError",
    "AnalyzerError",
    "SerializationError",
    "UnsupportedModelError",
]