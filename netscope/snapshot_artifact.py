"""
Snapshot artifact models.

Artifacts represent files or generated resources associated with a snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class SnapshotArtifact:
    """
    Immutable snapshot artifact descriptor.
    """

    name: str
    path: Path
    kind: str = "file"
    media_type: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Artifact name cannot be empty.")
        if not str(self.path).strip():
            raise ValueError("Artifact path cannot be empty.")
        if not self.kind.strip():
            raise ValueError("Artifact kind cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the artifact into a JSON-friendly dictionary.
        """

        return {
            "name": self.name,
            "path": str(self.path),
            "kind": self.kind,
            "media_type": self.media_type,
            "checksum": self.checksum,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "SnapshotArtifact",
]