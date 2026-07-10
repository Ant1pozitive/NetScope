"""
Generic registry implementation.

This module provides the low-level registry primitive used throughout NetScope.
Higher-level registry orchestration lives in `netscope.registries`.
"""

from __future__ import annotations

from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """
    A type-safe named object registry.

    The registry stores objects under string keys and supports idempotent
    replacement when explicitly requested.
    """

    def __init__(self) -> None:
        self._objects: dict[str, T] = {}

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Registry name cannot be empty.")
        return normalized

    def register(self, name: str, obj: T, *, overwrite: bool = False) -> T:
        """
        Register an object under a given name.

        Parameters
        ----------
        name:
            Registry key.
        obj:
            Object to store.
        overwrite:
            Replace an existing entry when set to True.
        """

        key = self._normalize_name(name)

        if key in self._objects and not overwrite:
            raise ValueError(f"Object '{key}' is already registered.")

        self._objects[key] = obj
        return obj

    def unregister(self, name: str) -> T:
        """
        Remove and return an object by name.
        """

        key = self._normalize_name(name)

        try:
            return self._objects.pop(key)
        except KeyError as exc:
            raise KeyError(f"Object '{key}' is not registered.") from exc

    def get(self, name: str) -> T:
        """
        Retrieve a registered object by name.
        """

        key = self._normalize_name(name)

        try:
            return self._objects[key]
        except KeyError as exc:
            raise KeyError(f"Object '{key}' is not registered.") from exc

    def try_get(self, name: str, default: T | None = None) -> T | None:
        """
        Retrieve a registered object by name or return a default value.
        """

        key = self._normalize_name(name)
        return self._objects.get(key, default)

    def contains(self, name: str) -> bool:
        """
        Return whether the registry contains a given name.
        """

        return self._normalize_name(name) in self._objects

    def clear(self) -> None:
        """
        Remove all registered objects.
        """

        self._objects.clear()

    def keys(self) -> KeysView[str]:
        """
        Return registry keys.
        """

        return self._objects.keys()

    def values(self) -> ValuesView[T]:
        """
        Return registry values.
        """

        return self._objects.values()

    def items(self) -> ItemsView[str, T]:
        """
        Return registry items.
        """

        return self._objects.items()

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __getitem__(self, name: str) -> T:
        return self.get(name)

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[T]:
        return iter(self._objects.values())


__all__ = [
    "Registry",
]