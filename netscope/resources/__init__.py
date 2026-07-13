"""
Resource management utilities for NetScope.

This package provides filesystem, caching, temporary directory, and workspace
abstractions used by the core runtime and future inspection pipeline.
"""

from __future__ import annotations

from .artifacts import ArtifactManager
from .cache import Cache
from .paths import PathResolver
from .tempdir import TempDirectory
from .workspace import Workspace

__all__ = [
    "ArtifactManager",
    "Cache",
    "PathResolver",
    "TempDirectory",
    "Workspace",
]