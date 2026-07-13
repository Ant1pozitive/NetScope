"""
Snapshot builder configuration.

This configuration controls what data is included in generated snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class SnapshotBuilderConfig:
    """
    Immutable configuration for the snapshot builder.
    """

    framework: str = "pytorch"
    snapshot_version: str = "0.1.0"
    include_session: bool = True
    include_context: bool = True
    include_environment: bool = True
    include_runtime_state: bool = True
    include_workspace: bool = True
    include_artifacts: bool = True
    include_target: bool = True
    include_diagnostics: bool = True
    auto_complete_metadata: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.framework.strip():
            raise ValueError("framework cannot be empty.")
        if not self.snapshot_version.strip():
            raise ValueError("snapshot_version cannot be empty.")


__all__ = [
    "SnapshotBuilderConfig",
]