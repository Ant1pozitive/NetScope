"""
Shared protocols.

Higher-level modules should depend on protocols instead of concrete
implementations whenever possible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .context import ExecutionContext
from .environment import Environment
from .lifecycle import ComponentState
from .resources import Workspace
from .session_config import SessionConfig
from .session_state import SessionState
from .state import RuntimeState


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
class ComponentProtocol(
    Named,
    Serializable,
    Resettable,
    Configurable,
    LifecycleAware,
    Protocol,
):
    @property
    def uid(self) -> str: ...


@runtime_checkable
class CollectorProtocol(ComponentProtocol, Protocol):
    def collect(
        self,
        model: Any,
        *,
        context: Any | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class AnalyzerProtocol(ComponentProtocol, Protocol):
    def analyze(
        self,
        target: Any,
        *,
        context: Any | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class PluginProtocol(ComponentProtocol, Protocol):
    def activate(self) -> Any: ...

    def deactivate(self) -> Any: ...


@runtime_checkable
class ExporterProtocol(ComponentProtocol, Protocol):
    def export(
        self,
        payload: Any,
        destination: Path | str,
        *,
        context: Any | None = None,
    ) -> Path: ...


@runtime_checkable
class SerializerProtocol(ComponentProtocol, Protocol):
    def serialize(
        self,
        payload: Any,
        *,
        context: Any | None = None,
    ) -> bytes: ...

    def deserialize(
        self,
        data: bytes,
        *,
        context: Any | None = None,
    ) -> Any: ...


@runtime_checkable
class SessionProtocol(ComponentProtocol, Protocol):
    @property
    def session_id(self) -> str: ...

    @property
    def session_state(self) -> SessionState: ...

    @property
    def context(self) -> ExecutionContext | None: ...

    @property
    def environment(self) -> Environment: ...

    @property
    def runtime_state(self) -> RuntimeState: ...

    @property
    def workspace(self) -> Workspace: ...

    @property
    def config(self) -> SessionConfig: ...

    def prepare(self) -> Any: ...

    def close(self) -> Any: ...


__all__ = [
    "Named",
    "Serializable",
    "Resettable",
    "Configurable",
    "LifecycleAware",
    "ComponentProtocol",
    "CollectorProtocol",
    "AnalyzerProtocol",
    "PluginProtocol",
    "ExporterProtocol",
    "SerializerProtocol",
    "SessionProtocol",
]