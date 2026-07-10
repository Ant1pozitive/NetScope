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


class ComponentError(NetScopeError):
    """Raised when a component fails."""


class ComponentLifecycleError(ComponentError):
    """Raised when an invalid lifecycle transition is requested."""


class ComponentDisposedError(ComponentError):
    """Raised when an operation targets a disposed component."""


__all__ = [
    "NetScopeError",
    "ConfigurationError",
    "SnapshotError",
    "HookError",
    "CollectorError",
    "AnalyzerError",
    "SerializationError",
    "UnsupportedModelError",
    "ComponentError",
    "ComponentLifecycleError",
    "ComponentDisposedError",
]