"""
Shared protocols.

Higher-level modules should depend on protocols instead of concrete
implementations whenever possible.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .lifecycle import ComponentState


class Named(Protocol):
    @property
    def name(self) -> str: ...


class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


class Resettable(Protocol):
    def reset(self) -> None: ...


class Configurable(Protocol):
    def configure(self, **kwargs: Any) -> None: ...


@runtime_checkable
class LifecycleAware(Protocol):
    @property
    def state(self) -> ComponentState: ...

    def initialize(self) -> Any: ...

    def start(self) -> Any: ...

    def stop(self) -> Any: ...

    def dispose(self) -> Any: ...


@runtime_checkable
class ComponentProtocol(Named, Serializable, Resettable, Configurable, LifecycleAware, Protocol):
    @property
    def uid(self) -> str: ...


__all__ = [
    "Named",
    "Serializable",
    "Resettable",
    "Configurable",
    "LifecycleAware",
    "ComponentProtocol",
]