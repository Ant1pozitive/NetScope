"""
Runtime series primitives.

A runtime series groups samples for one metric or telemetry stream.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from .runtime_metric_kind import RuntimeMetricKind
from .runtime_sample import RuntimeSample


@dataclass(slots=True, frozen=True)
class RuntimeSeries:
    """
    Immutable runtime series.
    """

    series_id: str
    name: str
    kind: RuntimeMetricKind = RuntimeMetricKind.CUSTOM
    samples: tuple[RuntimeSample, ...] = ()
    unit: str = ""
    scope: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        series_id = self.series_id.strip()
        name = self.name.strip()

        if not series_id:
            raise ValueError("series_id cannot be empty.")
        if not name:
            raise ValueError("name cannot be empty.")

        object.__setattr__(self, "series_id", series_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "unit", self.unit.strip())
        object.__setattr__(self, "scope", self.scope.strip())
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(self, "samples", tuple(self.samples))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def sample_count(self) -> int:
        """Return the number of samples in the series."""

        return len(self.samples)

    @property
    def is_empty(self) -> bool:
        """Return whether the series has no samples."""

        return self.sample_count == 0

    @property
    def first_timestamp(self) -> datetime | None:
        """Return the earliest sample timestamp."""

        if not self.samples:
            return None
        return min(sample.timestamp for sample in self.samples)

    @property
    def last_timestamp(self) -> datetime | None:
        """Return the latest sample timestamp."""

        if not self.samples:
            return None
        return max(sample.timestamp for sample in self.samples)

    @property
    def duration_seconds(self) -> float | None:
        """Return the duration covered by the series."""

        if self.first_timestamp is None or self.last_timestamp is None:
            return None
        return (self.last_timestamp - self.first_timestamp).total_seconds()

    @property
    def numeric_values(self) -> tuple[float, ...]:
        """Return numeric sample values."""

        return tuple(
            sample.numeric_value for sample in self.samples if sample.numeric_value is not None
        )

    @property
    def min_numeric_value(self) -> float | None:
        """Return the minimum numeric value."""

        values = self.numeric_values
        return min(values) if values else None

    @property
    def max_numeric_value(self) -> float | None:
        """Return the maximum numeric value."""

        values = self.numeric_values
        return max(values) if values else None

    @property
    def mean_numeric_value(self) -> float | None:
        """Return the mean numeric value."""

        values = self.numeric_values
        return (sum(values) / len(values)) if values else None

    @property
    def latest_sample(self) -> RuntimeSample | None:
        """Return the latest sample."""

        if not self.samples:
            return None
        return max(self.samples, key=lambda sample: sample.timestamp)

    def add_sample(self, sample: RuntimeSample) -> RuntimeSeries:
        """Return a copy with one additional sample."""

        return replace(self, samples=self.samples + (sample,))

    def extend_samples(
        self,
        samples: tuple[RuntimeSample, ...] | list[RuntimeSample],
    ) -> RuntimeSeries:
        """Return a copy with multiple additional samples."""

        return replace(self, samples=self.samples + tuple(samples))

    def filter_by_step(self, step: int) -> RuntimeSeries:
        """Return a copy containing only samples from a given step."""

        return replace(self, samples=tuple(sample for sample in self.samples if sample.step == step))

    def filter_by_tag(self, key: str, value: Any) -> RuntimeSeries:
        """Return a copy containing only samples with a matching tag."""

        return replace(
            self,
            samples=tuple(
                sample for sample in self.samples if sample.tags.get(key) == value
            ),
        )

    def with_metadata(self, **kwargs: Any) -> RuntimeSeries:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the series into a JSON-friendly dictionary."""

        return {
            "series_id": self.series_id,
            "name": self.name,
            "kind": self.kind.value,
            "sample_count": self.sample_count,
            "samples": [sample.to_dict() for sample in self.samples],
            "unit": self.unit,
            "scope": self.scope,
            "source": self.source,
            "first_timestamp": None if self.first_timestamp is None else self.first_timestamp.isoformat(),
            "last_timestamp": None if self.last_timestamp is None else self.last_timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "min_numeric_value": self.min_numeric_value,
            "max_numeric_value": self.max_numeric_value,
            "mean_numeric_value": self.mean_numeric_value,
            "metadata": dict(self.metadata),
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the series into JSON."""

        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """Persist the series to a JSON file."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path


__all__ = [
    "RuntimeSeries",
]