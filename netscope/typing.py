"""
Common typing aliases shared across the project.

Only project-wide aliases should be defined here.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

JsonPrimitive: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
)

JsonValue: TypeAlias = (
    JsonPrimitive
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)

JsonDict: TypeAlias = dict[str, JsonValue]

JsonList: TypeAlias = list[JsonValue]

PathLike: TypeAlias = str | Path

Metadata: TypeAlias = Mapping[str, Any]

MutableMetadata: TypeAlias = dict[str, Any]

Callback: TypeAlias = Callable[..., Any]

Predicate: TypeAlias = Callable[[Any], bool]

Factory: TypeAlias = Callable[..., Any]

IterableStr: TypeAlias = Iterable[str]

SequenceStr: TypeAlias = Sequence[str]

IteratorStr: TypeAlias = Iterator[str]

__all__ = [
    "JsonPrimitive",
    "JsonValue",
    "JsonDict",
    "JsonList",
    "PathLike",
    "Metadata",
    "MutableMetadata",
    "Callback",
    "Predicate",
    "Factory",
    "IterableStr",
    "SequenceStr",
    "IteratorStr",
]