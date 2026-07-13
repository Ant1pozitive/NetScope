"""
Artifact management utilities.

The artifact manager owns a root directory and provides convenience helpers
for writing text, bytes, JSON, and copied files in a consistent way.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

from .paths import PathResolver


@dataclass(slots=True)
class ArtifactManager:
    """
    Manage artifact files and a logical artifact index.
    """

    root: Path
    resolver: PathResolver | None = None
    create: bool = True
    _index: dict[str, Path] = field(default_factory=dict, init=False, repr=False)
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def __post_init__(self) -> None:
        self.root = self.root.expanduser().resolve()
        if self.create:
            self.root.mkdir(parents=True, exist_ok=True)
        if self.resolver is None:
            self.resolver = PathResolver.from_config(root=self.root)

    def _normalize_name(self, name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Artifact name cannot be empty.")
        return normalized

    def _resolve_path(self, destination: str | Path) -> Path:
        if self.resolver is None:
            return Path(destination).expanduser().resolve()
        path = self.resolver.resolve(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def register(self, name: str, path: str | Path, *, overwrite: bool = False) -> Path:
        """Register an existing artifact path under a logical name."""

        key = self._normalize_name(name)
        resolved = self._resolve_path(path)

        with self._lock:
            if key in self._index and not overwrite:
                raise ValueError(f"Artifact '{key}' is already registered.")
            self._index[key] = resolved
            return resolved

    def get(self, name: str) -> Path:
        """Return a registered artifact path."""

        key = self._normalize_name(name)
        with self._lock:
            try:
                return self._index[key]
            except KeyError as exc:
                raise KeyError(f"Artifact '{key}' is not registered.") from exc

    def contains(self, name: str) -> bool:
        """Return whether an artifact is registered."""

        key = self._normalize_name(name)
        with self._lock:
            return key in self._index

    def write_bytes(
        self,
        name: str,
        data: bytes,
        destination: str | Path,
        *,
        overwrite: bool = False,
    ) -> Path:
        """Write raw bytes to disk and register the artifact."""

        path = self._resolve_path(destination)

        if path.exists() and not overwrite:
            raise FileExistsError(f"Artifact already exists: {path}")

        path.write_bytes(data)
        return self.register(name, path, overwrite=True)

    def write_text(
        self,
        name: str,
        text: str,
        destination: str | Path,
        *,
        encoding: str = "utf-8",
        overwrite: bool = False,
    ) -> Path:
        """Write text to disk and register the artifact."""

        path = self._resolve_path(destination)

        if path.exists() and not overwrite:
            raise FileExistsError(f"Artifact already exists: {path}")

        path.write_text(text, encoding=encoding)
        return self.register(name, path, overwrite=True)

    def write_json(
        self,
        name: str,
        payload: Any,
        destination: str | Path,
        *,
        indent: int = 2,
        overwrite: bool = False,
    ) -> Path:
        """Write JSON data to disk and register the artifact."""

        text = json.dumps(payload, indent=indent, ensure_ascii=False, default=str)
        return self.write_text(
            name,
            text,
            destination,
            overwrite=overwrite,
        )

    def copy_file(
        self,
        name: str,
        source: str | Path,
        destination: str | Path,
        *,
        overwrite: bool = False,
    ) -> Path:
        """Copy a file and register it as an artifact."""

        source_path = Path(source).expanduser().resolve()
        destination_path = self._resolve_path(destination)

        if destination_path.exists() and not overwrite:
            raise FileExistsError(f"Artifact already exists: {destination_path}")

        shutil.copy2(source_path, destination_path)
        return self.register(name, destination_path, overwrite=True)

    def unregister(self, name: str) -> Path:
        """Remove an artifact from the logical index."""

        key = self._normalize_name(name)
        with self._lock:
            try:
                return self._index.pop(key)
            except KeyError as exc:
                raise KeyError(f"Artifact '{key}' is not registered.") from exc

    def clear(self) -> None:
        """Clear the logical index."""

        with self._lock:
            self._index.clear()

    def keys(self) -> KeysView[str]:
        with self._lock:
            return self._index.keys()

    def values(self) -> ValuesView[Path]:
        with self._lock:
            return self._index.values()

    def items(self) -> ItemsView[str, Path]:
        with self._lock:
            return self._index.items()

    def snapshot(self) -> dict[str, str]:
        """Return a lightweight snapshot of artifact registrations."""

        with self._lock:
            return {name: str(path) for name, path in self._index.items()}

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __len__(self) -> int:
        with self._lock:
            return len(self._index)

    def __iter__(self) -> Iterator[str]:
        with self._lock:
            return iter(tuple(self._index.keys()))