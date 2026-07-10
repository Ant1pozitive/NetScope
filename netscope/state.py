"""
Shared runtime state.

This module intentionally contains only lightweight state objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .context import ExecutionContext


@dataclass(slots=True)
class RuntimeState:
    """
    Mutable process-wide state for a NetScope session.
    """

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    session_id: str | None = None
    context: ExecutionContext | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)

    def attach_context(self, context: ExecutionContext) -> None:
        """Attach execution context to the runtime state."""

        self.context = context

    def set_flag(self, name: str, value: bool = True) -> None:
        """Set a boolean runtime flag."""

        self.flags[name] = value

    def get_flag(self, name: str, default: bool = False) -> bool:
        """Return a runtime flag value."""

        return self.flags.get(name, default)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the runtime state into a dictionary."""

        return {
            "started_at": self.started_at.isoformat(),
            "session_id": self.session_id,
            "context": None if self.context is None else self.context.to_dict(),
            "metadata": dict(self.metadata),
            "flags": dict(self.flags),
        }


GLOBAL_STATE = RuntimeState()