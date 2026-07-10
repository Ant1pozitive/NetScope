"""
Generic registry implementation.

Every plugin system inside NetScope is based on this registry.
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
                f"{name!r} is already registered."
            )

        self._objects[name] = obj

    def unregister(
        self,
        name: str,
    ) -> None:

        self._objects.pop(name)

    def get(
        self,
        name: str,
    ) -> T:

        return self._objects[name]

    def clear(self) -> None:

        self._objects.clear()

    def values(self):

        return self._objects.values()

    def items(self):

        return self._objects.items()

    def __contains__(self, name: str) -> bool:

        return name in self._objects

    def __len__(self) -> int:

        return len(self._objects)

    def __iter__(self) -> Iterator[T]:

        return iter(self._objects.values())