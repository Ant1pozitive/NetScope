"""
Workspace abstraction.

A workspace owns the root directories, artifact manager, temporary directory,
and runtime cache needed by diagnostics and future inspection flows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..component import BaseComponent
from ..context import ExecutionContext
from ..exceptions import ComponentDisposedError
from .artifacts import ArtifactManager
from .cache import Cache
from .paths import PathResolver
from .tempdir import TempDirectory


class Workspace(BaseComponent):
    """
    Central runtime workspace for NetScope.

    The workspace coordinates:
    - directory resolution
    - artifact persistence
    - in-memory caching
    - temporary working directories
    """

    def __init__(
        self,
        name: str = "workspace",
        *,
        context: ExecutionContext | None = None,
        root_dir: Path | None = None,
        cache_max_size: int = 1024,
        cache_ttl_seconds: float | None = None,
        keep_temp: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            metadata=metadata,
            context=context,
        )

        if root_dir is not None:
            self._resolver = PathResolver.from_config(root=root_dir)
        elif context is not None:
            self._resolver = PathResolver.from_config(root=context.root_dir)
        else:
            self._resolver = PathResolver.from_config()

        self._artifact_manager = ArtifactManager(root=self._resolver.artifacts_dir())
        self._cache: Cache[str, Any] = Cache(
            max_size=cache_max_size,
            ttl_seconds=cache_ttl_seconds,
        )
        self._tempdir: TempDirectory | None = None
        self._keep_temp = keep_temp

    @property
    def resolver(self) -> PathResolver:
        """Return the workspace path resolver."""

        return self._resolver

    @property
    def artifact_manager(self) -> ArtifactManager:
        """Return the workspace artifact manager."""

        return self._artifact_manager

    @property
    def cache(self) -> Cache[str, Any]:
        """Return the workspace cache."""

        return self._cache

    @property
    def tempdir(self) -> TempDirectory | None:
        """Return the current temporary directory, if any."""

        return self._tempdir

    @property
    def root_dir(self) -> Path:
        return self._resolver.root

    @property
    def report_dir(self) -> Path:
        return self._resolver.reports_dir()

    @property
    def artifact_dir(self) -> Path:
        return self._resolver.artifacts_dir()

    @property
    def snapshot_dir(self) -> Path:
        return self._resolver.snapshots_dir()

    def create_tempdir(self) -> TempDirectory:
        """
        Create a new managed temporary directory for the workspace.
        """

        if self._tempdir is not None and not self._tempdir.closed:
            return self._tempdir

        self._tempdir = TempDirectory(keep=self._keep_temp)
        return self._tempdir

    def cache_set(self, key: str, value: Any) -> None:
        """Store a value in the workspace cache."""

        self._cache.set(key, value)

    def cache_get(self, key: str, default: Any | None = None) -> Any | None:
        """Retrieve a value from the workspace cache."""

        return self._cache.get(key, default)

    def cache_delete(self, key: str) -> None:
        """Delete a cached value."""

        self._cache.delete(key)

    def cache_clear(self) -> None:
        """Clear the workspace cache."""

        self._cache.clear()

    def save_text(self, name: str, text: str, relative_path: str | Path) -> Path:
        """Save a text artifact inside the workspace."""

        return self._artifact_manager.write_text(name, text, relative_path)

    def save_bytes(self, name: str, data: bytes, relative_path: str | Path) -> Path:
        """Save a bytes artifact inside the workspace."""

        return self._artifact_manager.write_bytes(name, data, relative_path)

    def save_json(self, name: str, payload: Any, relative_path: str | Path) -> Path:
        """Save a JSON artifact inside the workspace."""

        return self._artifact_manager.write_json(name, payload, relative_path)

    def register_artifact(self, name: str, path: str | Path) -> Path:
        """Register an existing artifact path."""

        return self._artifact_manager.register(name, path, overwrite=True)

    def list_artifacts(self) -> tuple[str, ...]:
        """Return registered artifact names."""

        return tuple(sorted(self._artifact_manager.keys()))

    def artifact_snapshot(self) -> dict[str, str]:
        """Return a snapshot of registered artifacts."""

        return self._artifact_manager.snapshot()

    def _on_initialize(self) -> None:
        """Ensure workspace directories exist."""

        self._resolver.ensure_directories()
        self._artifact_manager.root.mkdir(parents=True, exist_ok=True)

    def _on_start(self) -> None:
        """Create a temporary working directory when the workspace starts."""

        self.create_tempdir()

    def _on_stop(self) -> None:
        """Cleanup the temporary directory when stopping."""

        if self._tempdir is not None:
            self._tempdir.cleanup()

    def _on_dispose(self) -> None:
        """Cleanup resources when the workspace is disposed."""

        self._cache.clear()
        if self._tempdir is not None:
            self._tempdir.cleanup()

    def dispose(self) -> Workspace:
        """
        Dispose the workspace and guard against repeated use.
        """

        super().dispose()
        return self

    def ensure_ready(self) -> None:
        """
        Ensure the workspace is initialized and usable.
        """

        if self.is_disposed:
            raise ComponentDisposedError(
                "Workspace has been disposed and can no longer be used."
            )

        if self.state.value == "created":
            self.initialize()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the workspace state."""

        return {
            **super().to_dict(),
            "resolver": self._resolver.to_dict(),
            "artifact_manager": self._artifact_manager.snapshot(),
            "cache": self._cache.stats(),
            "tempdir": None if self._tempdir is None else self._tempdir.to_dict(),
        }