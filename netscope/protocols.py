"""
Shared protocols.

Higher-level modules should depend on protocols instead of concrete
implementations whenever possible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .lifecycle import ComponentState
from .session_state import SessionState


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
    def context(self) -> Any | None: ...

    @property
    def environment(self) -> Any: ...

    @property
    def runtime_state(self) -> Any: ...

    @property
    def workspace(self) -> Any: ...

    def prepare(self) -> Any: ...

    def close(self) -> Any: ...

    def attach_manager(self, manager: Any) -> None: ...


@runtime_checkable
class InspectionResultProtocol(Serializable, Protocol):
    @property
    def inspection_id(self) -> str: ...

    @property
    def success(self) -> bool: ...

    @property
    def error(self) -> str | None: ...

    @property
    def session(self) -> dict[str, Any]: ...

    @property
    def target(self) -> dict[str, Any]: ...

    @property
    def metadata(self) -> dict[str, Any]: ...

    def summary(self) -> str: ...

    def to_json(self, *, indent: int = 2) -> str: ...

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path: ...


@runtime_checkable
class SnapshotProtocol(Serializable, Protocol):
    @property
    def snapshot_id(self) -> str: ...

    @property
    def session_id(self) -> str: ...

    @property
    def target_type(self) -> str: ...

    @property
    def is_completed(self) -> bool: ...

    def complete(self) -> Any: ...

    def with_section(self, name: str, payload: Any) -> Any: ...

    def to_json(self, *, indent: int = 2) -> str: ...

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path: ...


@runtime_checkable
class SnapshotBuilderProtocol(Protocol):
    def build(
        self,
        *,
        session: Any | None = None,
        result: Any | None = None,
        target: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...

    def from_session(
        self,
        session: Any,
        *,
        target: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...

    def from_result(
        self,
        result: Any,
        *,
        session: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...


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
    "InspectionResultProtocol",
    "SnapshotProtocol",
    "SnapshotBuilderProtocol",
]