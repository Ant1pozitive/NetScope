"""
Generic registry implementation.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):

    def __init__(self) -> None:
        self._objects: dict[str, T] = {}

    def register(
        self,
        name: str,
        obj: T,
    ) -> None:

        if name in self._objects:
            raise ValueError(
                f"Object '{name}' is already registered."
            )

        self._objects[name] = obj

    def unregister(self, name: str) -> None:
        self._objects.pop(name, None)

    def get(self, name: str) -> T:

        if name not in self._objects:
            raise KeyError(name)

        return self._objects[name]

    def contains(self, name: str) -> bool:
        return name in self._objects

    def clear(self) -> None:
        self._objects.clear()

    def keys(self):
        return self._objects.keys()

    def values(self):
        return self._objects.values()

    def items(self):
        return self._objects.items()

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._objects

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[T]:
        return iter(self._objects.values())