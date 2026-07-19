"""
Runtime metric primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .runtime_metric_kind import RuntimeMetricKind


@dataclass(slots=True, frozen=True)
class RuntimeMetric:
    """
    Immutable runtime metric descriptor.
    """

    metric_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    kind: RuntimeMetricKind = RuntimeMetricKind.CUSTOM
    value: Any = None
    unit: str = ""
    scope: str = ""
    source: str = ""
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        metric_id = self.metric_id.strip()
        name = self.name.strip()
        unit = self.unit.strip()
        scope = self.scope.strip()
        source = self.source.strip()

        if not metric_id:
            raise ValueError("metric_id cannot be empty.")
        if not name:
            raise ValueError("name cannot be empty.")

        object.__setattr__(self, "metric_id", metric_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def is_numeric(self) -> bool:
        """Return whether the metric value is numeric."""

        return isinstance(self.value, (int, float)) and not isinstance(self.value, bool)

    @property
    def numeric_value(self) -> float | None:
        """Return the metric as a float when possible."""

        if self.is_numeric:
            return float(self.value)
        return None

    def with_metadata(self, **kwargs: Any) -> RuntimeMetric:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the metric into a JSON-friendly dictionary."""

        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "kind": self.kind.value,
            "value": self._safe_value(self.value),
            "unit": self.unit,
            "scope": self.scope,
            "source": self.source,
            "collected_at": self.collected_at.isoformat(),
            "is_numeric": self.is_numeric,
            "numeric_value": self.numeric_value,
            "metadata": dict(self.metadata),
        }

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


__all__ = [
    "RuntimeMetric",
]