"""
Snapshot summary models.

The summary is a compact, human-oriented representation of what the snapshot
contains. It is intentionally sparse at this stage and will be enriched in
later phases by graph, hook, and collector outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(slots=True, frozen=True)
class SnapshotSummary:
    """
    High-level summary of a snapshot.
    """

    model_name: str = ""
    model_type: str = ""
    framework: str = "pytorch"
    num_parameters: int | None = None
    trainable_parameters: int | None = None
    num_buffers: int | None = None
    num_layers: int | None = None
    trainable_ratio: float | None = None
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.framework and not self.framework.strip():
            raise ValueError("framework cannot be empty.")

    @property
    def has_parameters(self) -> bool:
        """Return whether parameter statistics are available."""

        return self.num_parameters is not None

    def with_metadata(self, **kwargs: Any) -> SnapshotSummary:
        """
        Return a copy with merged metadata.
        """

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the summary into a JSON-friendly dictionary.
        """

        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "framework": self.framework,
            "num_parameters": self.num_parameters,
            "trainable_parameters": self.trainable_parameters,
            "num_buffers": self.num_buffers,
            "num_layers": self.num_layers,
            "trainable_ratio": self.trainable_ratio,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "SnapshotSummary",
]