"""
Collector batch primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .collector_kind import CollectorKind
from .collector_record import CollectorRecord


@dataclass(slots=True, frozen=True)
class CollectorBatch:
    """
    Immutable batch of collector records.
    """

    batch_id: str = field(default_factory=lambda: uuid4().hex)
    collector_name: str = "collector"
    collector_kind: CollectorKind = CollectorKind.CUSTOM
    records: tuple[CollectorRecord, ...] = ()
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise ValueError("batch_id cannot be empty.")
        if not self.collector_name.strip():
            raise ValueError("collector_name cannot be empty.")
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def record_count(self) -> int:
        """Return the number of records in the batch."""

        return len(self.records)

    @property
    def success_count(self) -> int:
        """Return the number of successful records."""

        return sum(1 for record in self.records if record.success)

    @property
    def failure_count(self) -> int:
        """Return the number of failed records."""

        return sum(1 for record in self.records if not record.success)

    @property
    def target_count(self) -> int:
        """Return the number of unique targets in the batch."""

        return len({record.target_id or record.target_name for record in self.records})

    @property
    def is_completed(self) -> bool:
        """Return whether the batch has been completed."""

        return self.finished_at is not None

    @property
    def duration_seconds(self) -> float | None:
        """Return the batch duration in seconds."""

        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    def add_record(self, record: CollectorRecord) -> CollectorBatch:
        """Return a copy with one additional record."""

        return replace(self, records=self.records + (record,))

    def extend_records(
        self,
        records: tuple[CollectorRecord, ...] | list[CollectorRecord],
    ) -> CollectorBatch:
        """Return a copy with multiple additional records."""

        return replace(self, records=self.records + tuple(records))

    def complete(
        self,
        *,
        finished_at: datetime | None = None,
    ) -> CollectorBatch:
        """Return a completed copy of the batch."""

        return replace(
            self,
            finished_at=finished_at or datetime.now(timezone.utc),
        )

    def with_metadata(self, **kwargs: Any) -> CollectorBatch:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the batch into a JSON-friendly dictionary."""

        return {
            "batch_id": self.batch_id,
            "collector_name": self.collector_name,
            "collector_kind": self.collector_kind.value,
            "records": [record.to_dict() for record in self.records],
            "record_count": self.record_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "target_count": self.target_count,
            "started_at": self.started_at.isoformat(),
            "finished_at": None if self.finished_at is None else self.finished_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "CollectorBatch",
]