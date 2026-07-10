"""
Convenience decorators for registry-based registration.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from .manager import GLOBAL_REGISTRY_MANAGER, RegistryManager

T = TypeVar("T")


def register(
    namespace: str,
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    """
    Decorator factory that registers an object in a namespace.
    """

    def decorator(obj: T) -> T:
        resolved_manager = manager or GLOBAL_REGISTRY_MANAGER
        resolved_name = name or getattr(obj, "__name__", obj.__class__.__name__)
        resolved_manager.register(
            namespace=namespace,
            name=resolved_name,
            obj=obj,
            overwrite=overwrite,
        )
        return obj

    return decorator


def component(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="component",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


def collector(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="collector",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


def analyzer(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="analyzer",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


def plugin(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="plugin",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


def exporter(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="exporter",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


def serializer(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="serializer",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


def hook(
    name: str | None = None,
    *,
    manager: RegistryManager | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    return register(
        namespace="hook",
        name=name,
        manager=manager,
        overwrite=overwrite,
    )


__all__ = [
    "register",
    "component",
    "collector",
    "analyzer",
    "plugin",
    "exporter",
    "serializer",
    "hook",
]