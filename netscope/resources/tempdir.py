"""
Temporary directory abstraction.

This wrapper provides explicit lifecycle management for temporary directories
used by runtime components and artifact generation.
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TempDirectory:
    """
    Managed temporary directory.

    The directory is created eagerly during initialization and cleaned up when
    `cleanup()` is called, unless `keep=True`.
    """

    prefix: str = "netscope-"
    suffix: str = ""
    dir: Path | None = None
    keep: bool = False
    _path: Path = field(init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        created = tempfile.mkdtemp(
            prefix=self.prefix,
            suffix=self.suffix,
            dir=None if self.dir is None else str(self.dir),
        )
        self._path = Path(created)

    @property
    def path(self) -> Path:
        """Return the temporary directory path."""

        return self._path

    @property
    def closed(self) -> bool:
        """Return whether the directory has been cleaned up."""

        return self._closed

    def exists(self) -> bool:
        """Return whether the directory still exists."""

        return self._path.exists()

    def cleanup(self) -> None:
        """Remove the directory unless keep=True."""

        if self._closed:
            return

        if not self.keep and self._path.exists():
            shutil.rmtree(self._path, ignore_errors=True)

        self._closed = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize the temporary directory state."""

        return {
            "path": str(self._path),
            "keep": self.keep,
            "closed": self._closed,
            "exists": self.exists(),
        }

    def __enter__(self) -> TempDirectory:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cleanup()

    def __fspath__(self) -> str:
        return str(self._path)

    def __truediv__(self, other: str | Path) -> Path:
        return self._path / other