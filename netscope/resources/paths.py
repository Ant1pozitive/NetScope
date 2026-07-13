"""
Path resolution helpers.

This module centralizes all filesystem path construction so that higher-level
components never hard-code workspace directories.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import CONFIG


@dataclass(slots=True, frozen=True)
class PathResolver:
    """
    Resolve project-relative and workspace-relative paths.

    Parameters are intentionally explicit to keep path handling predictable and
    easy to test.
    """

    root: Path = field(default_factory=lambda: CONFIG.config.paths.root.expanduser().resolve())
    reports_dirname: str = field(default_factory=lambda: CONFIG.config.paths.reports)
    artifacts_dirname: str = field(default_factory=lambda: CONFIG.config.paths.artifacts)
    snapshots_dirname: str = field(default_factory=lambda: CONFIG.config.paths.snapshots)

    @classmethod
    def from_config(cls, *, root: Path | None = None) -> PathResolver:
        """
        Build a resolver from the global configuration.
        """

        base_root = root if root is not None else CONFIG.config.paths.root
        resolved_root = base_root.expanduser().resolve()

        return cls(
            root=resolved_root,
            reports_dirname=CONFIG.config.paths.reports,
            artifacts_dirname=CONFIG.config.paths.artifacts,
            snapshots_dirname=CONFIG.config.paths.snapshots,
        )

    def resolve(self, path: str | Path) -> Path:
        """
        Resolve a path relative to the workspace root when needed.
        """

        candidate = Path(path).expanduser()

        if candidate.is_absolute():
            return candidate.resolve()

        return (self.root / candidate).resolve()

    def relative_to_root(self, path: str | Path) -> Path:
        """
        Return the path relative to the workspace root.

        Raises ValueError if the path does not belong to the root tree.
        """

        resolved = self.resolve(path)
        return resolved.relative_to(self.root)

    def reports_dir(self) -> Path:
        """Return the reports directory path."""

        return (self.root / self.reports_dirname).resolve()

    def artifacts_dir(self) -> Path:
        """Return the artifacts directory path."""

        return (self.root / self.artifacts_dirname).resolve()

    def snapshots_dir(self) -> Path:
        """Return the snapshots directory path."""

        return (self.root / self.snapshots_dirname).resolve()

    def ensure_directories(self) -> None:
        """
        Ensure that the canonical workspace directories exist.
        """

        self.root.mkdir(parents=True, exist_ok=True)
        self.reports_dir().mkdir(parents=True, exist_ok=True)
        self.artifacts_dir().mkdir(parents=True, exist_ok=True)
        self.snapshots_dir().mkdir(parents=True, exist_ok=True)

    def ensure_parent(self, path: str | Path) -> Path:
        """
        Ensure the parent directory for a file exists.
        """

        resolved = self.resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the resolver to a plain dictionary.
        """

        return {
            "root": str(self.root),
            "reports_dirname": self.reports_dirname,
            "artifacts_dirname": self.artifacts_dirname,
            "snapshots_dirname": self.snapshots_dirname,
            "reports_dir": str(self.reports_dir()),
            "artifacts_dir": str(self.artifacts_dir()),
            "snapshots_dir": str(self.snapshots_dir()),
        }