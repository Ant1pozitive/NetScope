"""
Base interfaces for NetScope extension points.

These classes define the minimal, shared contracts for collectors, analyzers,
plugins, exporters, and serializers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

from .component import BaseComponent
from .context import ExecutionContext


class BaseCollector(BaseComponent, ABC):
    """
    Base class for all collectors.

    Collectors are responsible for extracting raw observations from models,
    tensors, or runtime environments.
    """

    component_kind: ClassVar[str] = "collector"

    def __init__(
        self,
        name: str,
        *,
        namespace: str = "netscope",
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> None:
        super().__init__(
            name=name,
            namespace=namespace,
            version=version,
            metadata=metadata,
            context=context,
        )

    @abstractmethod
    def collect(
        self,
        model: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        """
        Collect raw data from a model or runtime target.
        """

    def __call__(
        self,
        model: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        return self.collect(model, context=context)


class BaseAnalyzer(BaseComponent, ABC):
    """
    Base class for all analyzers.

    Analyzers transform raw observations into findings, scores, diagnostics,
    or recommendations.
    """

    component_kind: ClassVar[str] = "analyzer"

    def __init__(
        self,
        name: str,
        *,
        namespace: str = "netscope",
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> None:
        super().__init__(
            name=name,
            namespace=namespace,
            version=version,
            metadata=metadata,
            context=context,
        )

    @abstractmethod
    def analyze(
        self,
        target: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        """
        Analyze a target object and return structured findings.
        """

    def __call__(
        self,
        target: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        return self.analyze(target, context=context)


class BasePlugin(BaseComponent, ABC):
    """
    Base class for all plugins.

    Plugins represent user-extensible runtime modules that can be activated,
    deactivated, and registered dynamically.
    """

    component_kind: ClassVar[str] = "plugin"

    def __init__(
        self,
        name: str,
        *,
        namespace: str = "netscope",
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> None:
        super().__init__(
            name=name,
            namespace=namespace,
            version=version,
            metadata=metadata,
            context=context,
        )

    def activate(self) -> BasePlugin:
        """
        Activate the plugin.

        The default implementation maps activation to the component lifecycle:
        initialize -> start.
        """

        self.initialize()
        self.start()
        return self

    def deactivate(self) -> BasePlugin:
        """
        Deactivate the plugin.

        The default implementation maps deactivation to stop.
        """

        self.stop()
        return self

    @property
    def is_active_plugin(self) -> bool:
        """Return whether the plugin is currently active."""

        return self.is_active


class BaseExporter(BaseComponent, ABC):
    """
    Base class for all exporters.

    Exporters transform structured payloads into persistent artifacts.
    """

    component_kind: ClassVar[str] = "exporter"

    def __init__(
        self,
        name: str,
        *,
        namespace: str = "netscope",
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> None:
        super().__init__(
            name=name,
            namespace=namespace,
            version=version,
            metadata=metadata,
            context=context,
        )

    @abstractmethod
    def export(
        self,
        payload: Any,
        destination: Path | str,
        *,
        context: ExecutionContext | None = None,
    ) -> Path:
        """
        Export a payload to a destination path.
        """

    def __call__(
        self,
        payload: Any,
        destination: Path | str,
        *,
        context: ExecutionContext | None = None,
    ) -> Path:
        return self.export(payload, destination, context=context)


class BaseSerializer(BaseComponent, ABC):
    """
    Base class for all serializers.

    Serializers convert payloads to and from bytes.
    """

    component_kind: ClassVar[str] = "serializer"

    def __init__(
        self,
        name: str,
        *,
        namespace: str = "netscope",
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> None:
        super().__init__(
            name=name,
            namespace=namespace,
            version=version,
            metadata=metadata,
            context=context,
        )

    @abstractmethod
    def serialize(
        self,
        payload: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> bytes:
        """
        Serialize a payload into bytes.
        """

    @abstractmethod
    def deserialize(
        self,
        data: bytes,
        *,
        context: ExecutionContext | None = None,
    ) -> Any:
        """
        Deserialize bytes into a Python object.
        """

    def dump(
        self,
        payload: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> bytes:
        """
        Convenience alias for serialize.
        """

        return self.serialize(payload, context=context)

    def load(
        self,
        data: bytes,
        *,
        context: ExecutionContext | None = None,
    ) -> Any:
        """
        Convenience alias for deserialize.
        """

        return self.deserialize(data, context=context)


__all__ = [
    "BaseCollector",
    "BaseAnalyzer",
    "BasePlugin",
    "BaseExporter",
    "BaseSerializer",
]