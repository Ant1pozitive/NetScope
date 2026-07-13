"""
Snapshot metadata models.

Snapshot metadata stores the immutable identity and timeline information for a
single diagnostic snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class SnapshotMetadata:
    """
    Immutable metadata for a snapshot.
    """

    snapshot_id: str = field(default_factory=lambda: uuid4().hex)
    inspector_name: str = "inspector"
    session_id: str = ""
    session_state: str = ""
    target_type: str = ""
    target_name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    version: str = "0.1.0"
    tags: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.snapshot_id.strip():
            raise ValueError("snapshot_id cannot be empty.")
        if not self.inspector_name.strip():
            raise ValueError("inspector_name cannot be empty.")
        if not self.version.strip():
            raise ValueError("version cannot be empty.")

    @property
    def is_completed(self) -> bool:
        """Return whether the snapshot has been marked as completed."""

        return self.completed_at is not None

    def complete(self, *, completed_at: datetime | None = None) -> SnapshotMetadata:
        """
        Return a completed copy of the metadata.
        """

        return replace(
            self,
            completed_at=completed_at or datetime.now(timezone.utc),
        )

    def with_tags(self, **kwargs: Any) -> SnapshotMetadata:
        """
        Return a copy with merged tags.
        """

        merged = dict(self.tags)
        merged.update(kwargs)
        return replace(self, tags=merged)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the metadata into a JSON-friendly dictionary.
        """

        return {
            "snapshot_id": self.snapshot_id,
            "inspector_name": self.inspector_name,
            "session_id": self.session_id,
            "session_state": self.session_state,
            "target_type": self.target_type,
            "target_name": self.target_name,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                None if self.completed_at is None else self.completed_at.isoformat()
            ),
            "version": self.version,
            "tags": dict(self.tags),
        }


__all__ = [
    "SnapshotMetadata",
]