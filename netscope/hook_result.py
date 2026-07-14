"""
Hook execution result primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .hook_event import HookEvent


@dataclass(slots=True, frozen=True)
class HookResult:
    """
    Immutable hook execution result.
    """

    result_id: str = field(default_factory=lambda: uuid4().hex)
    event: HookEvent | None = None
    success: bool = True
    return_value: Any = None
    error_type: str | None = None
    error_message: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.result_id.strip():
            raise ValueError("result_id cannot be empty.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def status(self) -> str:
        """Return a human-readable status."""

        return "success" if self.success else "failed"

    @property
    def duration_seconds(self) -> float:
        """Return the result duration in seconds."""

        return (self.finished_at - self.started_at).total_seconds()

    @property
    def event_id(self) -> str:
        """Return the associated event identifier."""

        if self.event is None:
            return ""
        return self.event.event_id

    @property
    def hook_name(self) -> str:
        """Return the associated hook name."""

        if self.event is None:
            return ""
        return self.event.hook_name

    def _safe_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, dict):
            return {str(key): self._safe_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._safe_value(item) for item in value]
        if isinstance(value, set):
            return [self._safe_value(item) for item in sorted(value, key=repr)]
        try:
            return repr(value)
        except Exception as exc:  # noqa: BLE001
            return f"<repr failed: {exc.__class__.__name__}>"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the hook result into a JSON-friendly dictionary."""

        return {
            "result_id": self.result_id,
            "event_id": self.event_id,
            "hook_name": self.hook_name,
            "status": self.status,
            "success": self.success,
            "return_value": self._safe_value(self.return_value),
            "error_type": self.error_type,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "HookResult",
]