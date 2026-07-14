"""
Collector record primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .collector_kind import CollectorKind
from .collector_target import CollectorTarget


@dataclass(slots=True, frozen=True)
class CollectorRecord:
    """
    Immutable collector record.
    """

    record_id: str = field(default_factory=lambda: uuid4().hex)
    collector_kind: CollectorKind = CollectorKind.CUSTOM
    target: CollectorTarget | None = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    value: Any = None
    value_type: str = ""
    error_type: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise ValueError("record_id cannot be empty.")
        object.__setattr__(self, "value_type", self.value_type.strip())
        object.__setattr__(self, "metadata", dict(self.metadata))

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

    @property
    def target_type(self) -> str:
        """Return the target type, if available."""

        if self.target is None:
            return ""
        return self.target.target_type

    @property
    def status(self) -> str:
        """Return a human-readable status."""

        return "success" if self.success else "failed"

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

    def with_metadata(self, **kwargs: Any) -> CollectorRecord:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the record into a JSON-friendly dictionary."""

        return {
            "record_id": self.record_id,
            "collector_kind": self.collector_kind.value,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "target_type": self.target_type,
            "target": None if self.target is None else self.target.to_dict(),
            "collected_at": self.collected_at.isoformat(),
            "status": self.status,
            "success": self.success,
            "value": self._safe_value(self.value),
            "value_type": self.value_type,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "CollectorRecord",
]