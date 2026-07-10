"""
Shared typing aliases.

Import aliases from this module instead of typing directly.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any, TypeAlias

JsonDict: TypeAlias = dict[str, Any]

JsonList: TypeAlias = list[Any]

PathLike: TypeAlias = str | Path

Metadata: TypeAlias = Mapping[str, Any]

MutableMetadata: TypeAlias = dict[str, Any]

Callback: TypeAlias = Callable[..., Any]

IterableStr: TypeAlias = Iterable[str]

__all__ = [
    "JsonDict",
    "JsonList",
    "PathLike",
    "Metadata",
    "MutableMetadata",
    "Callback",
    "IterableStr",
]