"""
NetScope.

Universal diagnostics platform for neural networks.
"""

from __future__ import annotations

from ._version import __version__
from .component import BaseComponent
from .config import CONFIG
from .context import ExecutionContext
from .identity import ComponentIdentity
from .lifecycle import ComponentState
from .state import GLOBAL_STATE, RuntimeState

__all__ = [
    "__version__",
    "CONFIG",
    "GLOBAL_STATE",
    "RuntimeState",
    "ExecutionContext",
    "BaseComponent",
    "ComponentIdentity",
    "ComponentState",
]