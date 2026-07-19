"""
Runtime sample primitives.

A runtime sample captures one point-in-time measurement for a runtime metric.
It is intentionally lightweight, immutable, and serialization-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .runtime_metric import RuntimeMetric
from .runtime_metric_kind import RuntimeMetricKind


@dataclass(slots=True, frozen=True)
class RuntimeSample:
    """
    Immutable point-in-time runtime measurement.
    """

    sample_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    kind: RuntimeMetricKind = RuntimeMetricKind.CUSTOM
    value: Any = None
    unit: str = ""
    scope: str = ""
    source: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    step: int | None = None
    batch_index: int | None = None
    iteration: int | None = None
    tags: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        sample_id = self.sample_id.strip()
        name = self.name.strip()
        unit = self.unit.strip()
        scope = self.scope.strip()
        source = self.source.strip()

        if not sample_id:
            raise ValueError("sample_id cannot be empty.")
        if not name:
            raise ValueError("name cannot be empty.")

        object.__setattr__(self, "sample_id", sample_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "tags", dict(self.tags))
        object.__setattr__(self, "metadata", dict(self.metadata))

        if self.step is not None and self.step < 0:
            raise ValueError("step cannot be negative.")
        if self.batch_index is not None and self.batch_index < 0:
            raise ValueError("batch_index cannot be negative.")
        if self.iteration is not None and self.iteration < 0:
            raise ValueError("iteration cannot be negative.")

    @classmethod
    def from_metric(
        cls,
        metric: RuntimeMetric,
        *,
        step: int | None = None,
        batch_index: int | None = None,
        iteration: int | None = None,
        tags: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RuntimeSample:
        """
        Build a runtime sample from a runtime metric.
        """

        return cls(
            name=metric.name,
            kind=metric.kind,
            value=metric.value,
            unit=metric.unit,
            scope=metric.scope,
            source=metric.source,
            timestamp=metric.collected_at,
            step=step,
            batch_index=batch_index,
            iteration=iteration,
            tags={} if tags is None else dict(tags),
            metadata={
                "metric_id": metric.metric_id,
                **dict(metric.metadata),
                **({} if metadata is None else dict(metadata)),
            },
        )

    @property
    def is_numeric(self) -> bool:
        """Return whether the sample value is numeric."""

        return isinstance(self.value, (int, float)) and not isinstance(self.value, bool)

    @property
    def numeric_value(self) -> float | None:
        """Return the sample value as a float when possible."""

        if self.is_numeric:
            return float(self.value)
        return None

    @property
    def has_step(self) -> bool:
        """Return whether the sample has a step index."""

        return self.step is not None

    @property
    def has_batch_index(self) -> bool:
        """Return whether the sample has a batch index."""

        return self.batch_index is not None

    @property
    def has_iteration(self) -> bool:
        """Return whether the sample has an iteration index."""

        return self.iteration is not None

    def with_metadata(self, **kwargs: Any) -> RuntimeSample:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def with_tags(self, **kwargs: Any) -> RuntimeSample:
        """Return a copy with merged tags."""

        merged = dict(self.tags)
        merged.update(kwargs)
        return replace(self, tags=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the sample into a JSON-friendly dictionary."""

        return {
            "sample_id": self.sample_id,
            "name": self.name,
            "kind": self.kind.value,
            "value": self._safe_value(self.value),
            "unit": self.unit,
            "scope": self.scope,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "step": self.step,
            "batch_index": self.batch_index,
            "iteration": self.iteration,
            "is_numeric": self.is_numeric,
            "numeric_value": self.numeric_value,
            "tags": dict(self.tags),
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
    "RuntimeSample",
]