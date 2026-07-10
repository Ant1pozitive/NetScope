"""
NetScope.

Universal diagnostics platform for neural networks.
"""

from __future__ import annotations

from ._version import __version__
from .component import BaseComponent
from .config import CONFIG
from .identity import ComponentIdentity
from .lifecycle import ComponentState

__all__ = [
    "__version__",
    "CONFIG",
    "BaseComponent",
    "ComponentIdentity",
    "ComponentState",
]