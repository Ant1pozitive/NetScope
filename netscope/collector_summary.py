"""
Collector summary primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .collector_batch import CollectorBatch
from .collector_kind import CollectorKind


@dataclass(slots=True, frozen=True)
class CollectorSummary:
    """
    Compact statistics for collector results.
    """

    collector_name: str = "collector"
    collector_kind: CollectorKind = CollectorKind.CUSTOM
    batch_count: int = 0
    record_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    target_count: int = 0
    first_collected_at: datetime | None = None
    last_collected_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.collector_name.strip():
            raise ValueError("collector_name cannot be empty.")
        if self.batch_count < 0:
            raise ValueError("batch_count cannot be negative.")
        if self.record_count < 0:
            raise ValueError("record_count cannot be negative.")
        if self.success_count < 0:
            raise ValueError("success_count cannot be negative.")
        if self.failure_count < 0:
            raise ValueError("failure_count cannot be negative.")
        if self.target_count < 0:
            raise ValueError("target_count cannot be negative.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def success_rate(self) -> float | None:
        """Return the success rate if records are present."""

        if self.record_count <= 0:
            return None
        return self.success_count / self.record_count

    @classmethod
    def from_batches(
        cls,
        *,
        collector_name: str,
        collector_kind: CollectorKind,
        batches: tuple[CollectorBatch, ...] | list[CollectorBatch],
        metadata: dict[str, Any] | None = None,
    ) -> CollectorSummary:
        """Build a summary from batches."""

        batch_tuple = tuple(batches)
        record_count = sum(batch.record_count for batch in batch_tuple)
        success_count = sum(batch.success_count for batch in batch_tuple)
        failure_count = sum(batch.failure_count for batch in batch_tuple)
        target_count = len(
            {
                record.target_id or record.target_name
                for batch in batch_tuple
                for record in batch.records
            }
        )

        collected_times = [
            record.collected_at
            for batch in batch_tuple
            for record in batch.records
        ]
        first_collected_at = min(collected_times) if collected_times else None
        last_collected_at = max(collected_times) if collected_times else None

        return cls(
            collector_name=collector_name,
            collector_kind=collector_kind,
            batch_count=len(batch_tuple),
            record_count=record_count,
            success_count=success_count,
            failure_count=failure_count,
            target_count=target_count,
            first_collected_at=first_collected_at,
            last_collected_at=last_collected_at,
            metadata={} if metadata is None else dict(metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the summary into a JSON-friendly dictionary."""

        return {
            "collector_name": self.collector_name,
            "collector_kind": self.collector_kind.value,
            "batch_count": self.batch_count,
            "record_count": self.record_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "target_count": self.target_count,
            "success_rate": self.success_rate,
            "first_collected_at": (
                None if self.first_collected_at is None else self.first_collected_at.isoformat()
            ),
            "last_collected_at": (
                None if self.last_collected_at is None else self.last_collected_at.isoformat()
            ),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "CollectorSummary",
]