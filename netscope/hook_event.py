"""
Hook event primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .hook_kind import HookKind
from .hook_target import HookTarget


@dataclass(slots=True, frozen=True)
class HookEvent:
    """
    Immutable hook event descriptor.
    """

    event_id: str = field(default_factory=lambda: uuid4().hex)
    hook_kind: HookKind = HookKind.FORWARD
    hook_name: str = ""
    target: HookTarget | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    phase: str = "runtime"
    metadata: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id cannot be empty.")
        if not self.hook_name.strip():
            object.__setattr__(self, "hook_name", self.hook_kind.value)
        object.__setattr__(self, "phase", self.phase.strip() or "runtime")
        object.__setattr__(self, "metadata", dict(self.metadata))
        object.__setattr__(self, "payload", dict(self.payload))

    @property
    def target_id(self) -> str:
        """Return the target identifier, if available."""

        if self.target is None:
            return ""
        return self.target.target_id

    @property
    def target_name(self) -> str:
        """Return the target name, if available."""

        if self.target is None:
            return ""
        return self.target.name

    def with_metadata(self, **kwargs: Any) -> HookEvent:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def with_payload(self, **kwargs: Any) -> HookEvent:
        """Return a copy with merged payload."""

        merged = dict(self.payload)
        merged.update(kwargs)
        return replace(self, payload=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event into a JSON-friendly dictionary."""

        return {
            "event_id": self.event_id,
            "hook_kind": self.hook_kind.value,
            "hook_name": self.hook_name,
            "phase": self.phase,
            "created_at": self.created_at.isoformat(),
            "target_id": self.target_id,
            "target_name": self.target_name,
            "target": None if self.target is None else self.target.to_dict(),
            "metadata": dict(self.metadata),
            "payload": dict(self.payload),
        }


__all__ = [
    "HookEvent",
]