"""
Shared runtime state.

This module intentionally contains only lightweight state objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RuntimeState:

    started_at: datetime = field(default_factory=datetime.utcnow)

    metadata: dict[str, Any] = field(default_factory=dict)

    flags: dict[str, bool] = field(default_factory=dict)


GLOBAL_STATE = RuntimeState()