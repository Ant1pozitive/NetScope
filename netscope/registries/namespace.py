"""
Namespace-aware registry wrapper.

Each namespace groups related registrations such as collectors, analyzers,
plugins, exporters, or hooks.
"""

from __future__ import annotations

from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from dataclasses import dataclass, field
from typing import Any

from ..registry import Registry


@dataclass(slots=True)
class NamespaceRegistry:
    """
    Container for a single namespace.

    Examples of namespaces:
    - component
    - collector
    - analyzer
    - plugin
    - exporter
    - serializer
    - hook
    """

    namespace: str
    _registry: Registry[Any] = field(default_factory=Registry)

    def __post_init__(self) -> None:
        self.namespace = self._normalize_name(self.namespace)

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Namespace name cannot be empty.")
        return normalized

    def register(self, name: str, obj: Any, *, overwrite: bool = False) -> Any:
        """
        Register an object within the namespace.
        """

        return self._registry.register(name, obj, overwrite=overwrite)

    def unregister(self, name: str) -> Any:
        """
        Remove and return an object from the namespace.
        """

        return self._registry.unregister(name)

    def get(self, name: str) -> Any:
        """
        Retrieve an object from the namespace.
        """

        return self._registry.get(name)

    def try_get(self, name: str, default: Any | None = None) -> Any | None:
        """
        Retrieve an object or return a default value.
        """

        return self._registry.try_get(name, default)

    def contains(self, name: str) -> bool:
        """
        Return whether the namespace contains a registered object.
        """

        return self._registry.contains(name)

    def clear(self) -> None:
        """
        Clear the namespace registry.
        """

        self._registry.clear()

    def keys(self) -> KeysView[str]:
        return self._registry.keys()

    def values(self) -> ValuesView[Any]:
        return self._registry.values()

    def items(self) -> ItemsView[str, Any]:
        return self._registry.items()

    def snapshot(self) -> dict[str, str]:
        """
        Return a lightweight snapshot of registered names.

        The snapshot maps registration names to type names.
        """

        return {
            name: type(obj).__name__
            for name, obj in self._registry.items()
        }

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __len__(self) -> int:
        return len(self._registry)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._registry)


__all__ = [
    "NamespaceRegistry",
]