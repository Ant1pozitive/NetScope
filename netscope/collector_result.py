"""
Collector result primitives.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .collector_batch import CollectorBatch
from .collector_kind import CollectorKind
from .collector_summary import CollectorSummary


@dataclass(slots=True, frozen=True)
class CollectorResult:
    """
    Immutable result returned by a collector.
    """

    result_id: str = field(default_factory=lambda: uuid4().hex)
    collector_name: str = "collector"
    collector_kind: CollectorKind = CollectorKind.CUSTOM
    batches: tuple[CollectorBatch, ...] = ()
    summary: CollectorSummary | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.result_id.strip():
            raise ValueError("result_id cannot be empty.")
        if not self.collector_name.strip():
            raise ValueError("collector_name cannot be empty.")
        object.__setattr__(self, "batches", tuple(self.batches))
        object.__setattr__(self, "metadata", dict(self.metadata))
        if self.summary is None:
            object.__setattr__(
                self,
                "summary",
                CollectorSummary.from_batches(
                    collector_name=self.collector_name,
                    collector_kind=self.collector_kind,
                    batches=self.batches,
                    metadata=self.metadata,
                ),
            )

    @property
    def batch_count(self) -> int:
        """Return the number of batches."""

        return len(self.batches)

    @property
    def record_count(self) -> int:
        """Return the number of records across all batches."""

        return sum(batch.record_count for batch in self.batches)

    @property
    def success_rate(self) -> float | None:
        """Return the aggregated success rate."""

        return self.summary.success_rate

    @property
    def is_empty(self) -> bool:
        """Return whether the result contains any records."""

        return self.record_count == 0

    @property
    def records(self) -> tuple[Any, ...]:
        """Return all records from all batches."""

        return tuple(
            record
            for batch in self.batches
            for record in batch.records
        )

    def with_metadata(self, **kwargs: Any) -> CollectorResult:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def add_batch(self, batch: CollectorBatch) -> CollectorResult:
        """Return a copy with one additional batch."""

        batches = self.batches + (batch,)
        return CollectorResult(
            result_id=self.result_id,
            collector_name=self.collector_name,
            collector_kind=self.collector_kind,
            batches=batches,
            summary=CollectorSummary.from_batches(
                collector_name=self.collector_name,
                collector_kind=self.collector_kind,
                batches=batches,
                metadata=self.metadata,
            ),
            created_at=self.created_at,
            metadata=dict(self.metadata),
        )

    def extend_batches(
        self,
        batches: tuple[CollectorBatch, ...] | list[CollectorBatch],
    ) -> CollectorResult:
        """Return a copy with multiple additional batches."""

        return CollectorResult(
            result_id=self.result_id,
            collector_name=self.collector_name,
            collector_kind=self.collector_kind,
            batches=self.batches + tuple(batches),
            summary=CollectorSummary.from_batches(
                collector_name=self.collector_name,
                collector_kind=self.collector_kind,
                batches=self.batches + tuple(batches),
                metadata=self.metadata,
            ),
            created_at=self.created_at,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the result into a JSON-friendly dictionary."""

        return {
            "result_id": self.result_id,
            "collector_name": self.collector_name,
            "collector_kind": self.collector_kind.value,
            "batch_count": self.batch_count,
            "record_count": self.record_count,
            "success_rate": self.success_rate,
            "is_empty": self.is_empty,
            "batches": [batch.to_dict() for batch in self.batches],
            "summary": self.summary.to_dict() if self.summary is not None else None,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the collector result into JSON."""

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """Persist the collector result to a JSON file."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path


__all__ = [
    "CollectorResult",
]