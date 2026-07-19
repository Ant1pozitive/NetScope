"""
Runtime snapshot primitives.

A runtime snapshot captures a structured telemetry state at a point in time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .runtime_metric import RuntimeMetric
from .runtime_sample import RuntimeSample
from .runtime_series import RuntimeSeries
from .runtime_summary import RuntimeSummary


@dataclass(slots=True, frozen=True)
class RuntimeSnapshot:
    """
    Immutable runtime snapshot.
    """

    snapshot_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "runtime_snapshot"
    metrics: tuple[RuntimeMetric, ...] = ()
    samples: tuple[RuntimeSample, ...] = ()
    series: tuple[RuntimeSeries, ...] = ()
    summary: RuntimeSummary | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        snapshot_id = self.snapshot_id.strip()
        name = self.name.strip()

        if not snapshot_id:
            raise ValueError("snapshot_id cannot be empty.")
        if not name:
            raise ValueError("name cannot be empty.")

        object.__setattr__(self, "snapshot_id", snapshot_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "metrics", tuple(self.metrics))
        object.__setattr__(self, "samples", tuple(self.samples))
        object.__setattr__(self, "series", tuple(self.series))
        object.__setattr__(self, "metadata", dict(self.metadata))

        if self.summary is None:
            object.__setattr__(
                self,
                "summary",
                self._build_summary(),
            )

    @property
    def is_completed(self) -> bool:
        """Return whether the snapshot has been completed."""

        return self.completed_at is not None

    @property
    def metric_count(self) -> int:
        """Return the number of metrics."""

        return len(self.metrics)

    @property
    def sample_count(self) -> int:
        """Return the number of samples."""

        return len(self.samples)

    @property
    def series_count(self) -> int:
        """Return the number of series."""

        return len(self.series)

    @property
    def duration_seconds(self) -> float | None:
        """Return the lifetime between creation and completion."""

        if self.completed_at is None:
            return None
        return (self.completed_at - self.created_at).total_seconds()

    def complete(self, *, completed_at: datetime | None = None) -> RuntimeSnapshot:
        """Return a completed copy of the snapshot."""

        return replace(
            self,
            completed_at=completed_at or datetime.now(timezone.utc),
        )

    def add_metric(self, metric: RuntimeMetric) -> RuntimeSnapshot:
        """Return a copy with one additional metric."""

        metrics = self.metrics + (metric,)
        return replace(self, metrics=metrics, summary=self._build_summary(metrics=metrics))

    def add_sample(self, sample: RuntimeSample) -> RuntimeSnapshot:
        """Return a copy with one additional sample."""

        samples = self.samples + (sample,)
        return replace(self, samples=samples, summary=self._build_summary(samples=samples))

    def add_series(self, runtime_series: RuntimeSeries) -> RuntimeSnapshot:
        """Return a copy with one additional series."""

        series = self.series + (runtime_series,)
        return replace(self, series=series, summary=self._build_summary(series=series))

    def extend_metrics(
        self,
        metrics: tuple[RuntimeMetric, ...] | list[RuntimeMetric],
    ) -> RuntimeSnapshot:
        """Return a copy with multiple additional metrics."""

        combined = self.metrics + tuple(metrics)
        return replace(self, metrics=combined, summary=self._build_summary(metrics=combined))

    def extend_samples(
        self,
        samples: tuple[RuntimeSample, ...] | list[RuntimeSample],
    ) -> RuntimeSnapshot:
        """Return a copy with multiple additional samples."""

        combined = self.samples + tuple(samples)
        return replace(self, samples=combined, summary=self._build_summary(samples=combined))

    def extend_series(
        self,
        series: tuple[RuntimeSeries, ...] | list[RuntimeSeries],
    ) -> RuntimeSnapshot:
        """Return a copy with multiple additional series."""

        combined = self.series + tuple(series)
        return replace(self, series=combined, summary=self._build_summary(series=combined))

    def with_metadata(self, **kwargs: Any) -> RuntimeSnapshot:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def _build_summary(
        self,
        *,
        metrics: tuple[RuntimeMetric, ...] | list[RuntimeMetric] | None = None,
        samples: tuple[RuntimeSample, ...] | list[RuntimeSample] | None = None,
        series: tuple[RuntimeSeries, ...] | list[RuntimeSeries] | None = None,
    ) -> RuntimeSummary:
        """Build a runtime summary from available data."""

        metrics_tuple = self.metrics if metrics is None else tuple(metrics)
        samples_tuple = self.samples if samples is None else tuple(samples)
        series_tuple = self.series if series is None else tuple(series)

        numeric_values = [
            value
            for value in (
                *(metric.numeric_value for metric in metrics_tuple),
                *(sample.numeric_value for sample in samples_tuple),
                *(runtime_series.mean_numeric_value for runtime_series in series_tuple),
            )
            if value is not None
        ]

        tensor_metric_count = sum(
            1
            for metric in metrics_tuple
            if metric.kind.value in {"gpu", "vram"} and metric.is_numeric is False
        )

        return RuntimeSummary(
            collector_name=self.name,
            metric_count=len(metrics_tuple),
            numeric_metric_count=sum(1 for metric in metrics_tuple if metric.numeric_value is not None)
            + sum(1 for sample in samples_tuple if sample.numeric_value is not None)
            + sum(1 for runtime_series in series_tuple if runtime_series.mean_numeric_value is not None),
            tensor_metric_count=tensor_metric_count,
            non_numeric_metric_count=sum(1 for metric in metrics_tuple if metric.numeric_value is None)
            + sum(1 for sample in samples_tuple if sample.numeric_value is None)
            + sum(1 for runtime_series in series_tuple if runtime_series.mean_numeric_value is None),
            metric_names=tuple(metric.name for metric in metrics_tuple),
            min_numeric_value=min(numeric_values) if numeric_values else None,
            max_numeric_value=max(numeric_values) if numeric_values else None,
            mean_numeric_value=(sum(numeric_values) / len(numeric_values)) if numeric_values else None,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the snapshot into a JSON-friendly dictionary."""

        return {
            "snapshot_id": self.snapshot_id,
            "name": self.name,
            "metric_count": self.metric_count,
            "sample_count": self.sample_count,
            "series_count": self.series_count,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "samples": [sample.to_dict() for sample in self.samples],
            "series": [runtime_series.to_dict() for runtime_series in self.series],
            "summary": self.summary.to_dict() if self.summary is not None else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": None if self.completed_at is None else self.completed_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "is_completed": self.is_completed,
            "metadata": dict(self.metadata),
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the snapshot into JSON."""

        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """Persist the snapshot to a JSON file."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path


__all__ = [
    "RuntimeSnapshot",
]