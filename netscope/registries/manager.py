"""
Registry manager.

The manager orchestrates multiple namespace registries and provides a single
entry point for object registration and lookup.
"""

from __future__ import annotations

from collections.abc import Iterable
from threading import RLock
from typing import Any

from .namespace import NamespaceRegistry


class RegistryManager:
    """
    Manage multiple namespace registries in a thread-safe manner.
    """

    def __init__(self) -> None:
        self._namespaces: dict[str, NamespaceRegistry] = {}
        self._lock = RLock()

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Registry name cannot be empty.")
        return normalized

    def ensure_namespace(self, namespace: str) -> NamespaceRegistry:
        """
        Return an existing namespace registry or create a new one.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            registry = self._namespaces.get(key)
            if registry is None:
                registry = NamespaceRegistry(namespace=key)
                self._namespaces[key] = registry
            return registry

    def register(
        self,
        namespace: str,
        name: str,
        obj: Any,
        *,
        overwrite: bool = False,
    ) -> Any:
        """
        Register an object in a namespace.
        """

        with self._lock:
            registry = self.ensure_namespace(namespace)
            return registry.register(name, obj, overwrite=overwrite)

    def unregister(self, namespace: str, name: str) -> Any:
        """
        Remove an object from a namespace.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            registry = self._namespaces[key]
            value = registry.unregister(name)

            if len(registry) == 0:
                self._namespaces.pop(key, None)

            return value

    def get(self, namespace: str, name: str) -> Any:
        """
        Retrieve an object from a namespace.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            return self._namespaces[key].get(name)

    def try_get(
        self,
        namespace: str,
        name: str,
        default: Any | None = None,
    ) -> Any | None:
        """
        Retrieve an object or return a default value.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            registry = self._namespaces.get(key)
            if registry is None:
                return default
            return registry.try_get(name, default)

    def contains(self, namespace: str, name: str) -> bool:
        """
        Return whether the registry manager contains the object.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            registry = self._namespaces.get(key)
            return registry.contains(name) if registry is not None else False

    def has_namespace(self, namespace: str) -> bool:
        """
        Return whether a namespace exists.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            return key in self._namespaces

    def list_namespaces(self) -> tuple[str, ...]:
        """
        Return all namespaces.
        """

        with self._lock:
            return tuple(sorted(self._namespaces.keys()))

    def list(self, namespace: str) -> tuple[str, ...]:
        """
        Return all names registered under a namespace.
        """

        key = self._normalize_name(namespace)

        with self._lock:
            registry = self._namespaces[key]
            return tuple(sorted(registry.keys()))

    def snapshot(self) -> dict[str, dict[str, str]]:
        """
        Return a lightweight snapshot of all namespaces.
        """

        with self._lock:
            return {
                namespace: registry.snapshot()
                for namespace, registry in self._namespaces.items()
            }

    def clear(self, namespace: str | None = None) -> None:
        """
        Clear a namespace or the entire manager.
        """

        with self._lock:
            if namespace is None:
                self._namespaces.clear()
                return

            key = self._normalize_name(namespace)
            self._namespaces.pop(key, None)

    def extend(
        self,
        namespace: str,
        items: Iterable[tuple[str, Any]],
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a batch of objects in a namespace.
        """

        for name, obj in items:
            self.register(namespace, name, obj, overwrite=overwrite)


GLOBAL_REGISTRY_MANAGER = RegistryManager()

__all__ = [
    "RegistryManager",
    "GLOBAL_REGISTRY_MANAGER",
]