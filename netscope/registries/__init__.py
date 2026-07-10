"""
Registry infrastructure for NetScope.

This package provides namespace-aware registries, a global registry manager,
and convenience decorators for object registration.
"""

from __future__ import annotations

from .decorators import (
    analyzer,
    collector,
    component,
    exporter,
    hook,
    plugin,
    register,
    serializer,
)
from .manager import GLOBAL_REGISTRY_MANAGER, RegistryManager
from .namespace import NamespaceRegistry

__all__ = [
    "NamespaceRegistry",
    "RegistryManager",
    "GLOBAL_REGISTRY_MANAGER",
    "register",
    "component",
    "collector",
    "analyzer",
    "plugin",
    "exporter",
    "serializer",
    "hook",
]