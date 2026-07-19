"""
Runtime summary primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .runtime_metric import RuntimeMetric


@dataclass(slots=True, frozen=True)
class RuntimeSummary:
    """
    Compact runtime telemetry summary.
    """

    collector_name: str = "runtime_collector"
    metric_count: int = 0
    numeric_metric_count: int = 0
    tensor_metric_count: int = 0
    non_numeric_metric_count: int = 0
    metric_names: tuple[str, ...] = ()
    min_numeric_value: float | None = None
    max_numeric_value: float | None = None
    mean_numeric_value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.collector_name.strip():
            raise ValueError("collector_name cannot be empty.")
        object.__setattr__(self, "metric_names", tuple(self.metric_names))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def numeric_value_range(self) -> float | None:
        """Return the numeric range if available."""

        if self.min_numeric_value is None or self.max_numeric_value is None:
            return None
        return self.max_numeric_value - self.min_numeric_value

    @classmethod
    def from_metrics(
        cls,
        *,
        collector_name: str,
        metrics: tuple[RuntimeMetric, ...] | list[RuntimeMetric],
        metadata: dict[str, Any] | None = None,
    ) -> RuntimeSummary:
        """
        Build a summary from runtime metrics.
        """

        metric_tuple = tuple(metrics)
        numeric_values = [metric.numeric_value for metric in metric_tuple if metric.numeric_value is not None]
        tensor_metric_count = sum(1 for metric in metric_tuple if metric.kind.value in {"gpu", "vram"} and metric.is_numeric is False)
        non_numeric_metric_count = sum(1 for metric in metric_tuple if not metric.is_numeric)

        return cls(
            collector_name=collector_name,
            metric_count=len(metric_tuple),
            numeric_metric_count=len(numeric_values),
            tensor_metric_count=tensor_metric_count,
            non_numeric_metric_count=non_numeric_metric_count,
            metric_names=tuple(metric.name for metric in metric_tuple),
            min_numeric_value=min(numeric_values) if numeric_values else None,
            max_numeric_value=max(numeric_values) if numeric_values else None,
            mean_numeric_value=(sum(numeric_values) / len(numeric_values)) if numeric_values else None,
            metadata={} if metadata is None else dict(metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the summary into a JSON-friendly dictionary."""

        return {
            "collector_name": self.collector_name,
            "metric_count": self.metric_count,
            "numeric_metric_count": self.numeric_metric_count,
            "tensor_metric_count": self.tensor_metric_count,
            "non_numeric_metric_count": self.non_numeric_metric_count,
            "metric_names": list(self.metric_names),
            "min_numeric_value": self.min_numeric_value,
            "max_numeric_value": self.max_numeric_value,
            "mean_numeric_value": self.mean_numeric_value,
            "numeric_value_range": self.numeric_value_range,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "RuntimeSummary",
]