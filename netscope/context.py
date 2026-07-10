"""
Execution context primitives.

The execution context carries environment- and task-specific information
required by components, collectors, and analyzers.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from .config import CONFIG
from .enums import DeviceType, ExecutionMode
from .exceptions import ConfigurationError


@dataclass(slots=True, frozen=True)
class ExecutionContext:
    """
    Immutable execution context for a NetScope session.
    """

    mode: ExecutionMode = ExecutionMode.INFERENCE
    device: DeviceType = DeviceType.CPU
    seed: int | None = None
    root_dir: Path = field(default_factory=Path.cwd)
    report_dir: Path = field(default_factory=lambda: Path.cwd() / "reports")
    artifact_dir: Path = field(default_factory=lambda: Path.cwd() / "artifacts")
    snapshot_dir: Path = field(default_factory=lambda: Path.cwd() / "snapshots")
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.seed is not None and self.seed < 0:
            raise ConfigurationError("Seed must be a non-negative integer.")
        if not self.root_dir.exists():
            raise ConfigurationError(
                f"Root directory does not exist: {self.root_dir}"
            )

    @classmethod
    def from_config(
        cls,
        *,
        mode: ExecutionMode = ExecutionMode.INFERENCE,
        device: DeviceType = DeviceType.CPU,
        seed: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionContext:
        """
        Build a context from global configuration.
        """

        paths = CONFIG.config.paths
        root = paths.root.expanduser().resolve()

        return cls(
            mode=mode,
            device=device,
            seed=seed,
            root_dir=root,
            report_dir=(root / paths.reports),
            artifact_dir=(root / paths.artifacts),
            snapshot_dir=(root / paths.snapshots),
            metadata=dict(metadata or {}),
        )

    def with_mode(self, mode: ExecutionMode) -> ExecutionContext:
        """Return a copy with updated execution mode."""

        return replace(self, mode=mode)

    def with_device(self, device: DeviceType) -> ExecutionContext:
        """Return a copy with updated execution device."""

        return replace(self, device=device)

    def with_seed(self, seed: int | None) -> ExecutionContext:
        """Return a copy with updated seed."""

        return replace(self, seed=seed)

    def with_metadata(self, **kwargs: Any) -> ExecutionContext:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def ensure_directories(self) -> None:
        """Create required directories if they do not exist."""

        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the context into a plain dictionary."""

        return {
            "mode": self.mode.value,
            "device": self.device.value,
            "seed": self.seed,
            "root_dir": str(self.root_dir),
            "report_dir": str(self.report_dir),
            "artifact_dir": str(self.artifact_dir),
            "snapshot_dir": str(self.snapshot_dir),
            "metadata": dict(self.metadata),
        }