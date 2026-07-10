"""
NetScope.

Universal diagnostics platform for neural networks.
"""

from __future__ import annotations

from ._version import __version__
from .component import BaseComponent
from .config import CONFIG
from .context import ExecutionContext
from .identity import ComponentIdentity
from .interfaces import (
    BaseAnalyzer,
    BaseCollector,
    BaseExporter,
    BasePlugin,
    BaseSerializer,
)
from .lifecycle import ComponentState
from .protocols import (
    AnalyzerProtocol,
    CollectorProtocol,
    ComponentProtocol,
    Configurable,
    ExporterProtocol,
    LifecycleAware,
    Named,
    PluginProtocol,
    Resettable,
    Serializable,
    SerializerProtocol,
)
from .registry import Registry
from .registries import (
    GLOBAL_REGISTRY_MANAGER,
    NamespaceRegistry,
    RegistryManager,
    analyzer,
    collector,
    component,
    exporter,
    hook,
    plugin,
    register,
    serializer,
)
from .state import GLOBAL_STATE, RuntimeState

__all__ = [
    "__version__",
    "CONFIG",
    "GLOBAL_STATE",
    "RuntimeState",
    "ExecutionContext",
    "BaseComponent",
    "ComponentIdentity",
    "ComponentState",
    "Registry",
    "NamespaceRegistry",
    "RegistryManager",
    "GLOBAL_REGISTRY_MANAGER",
    "register",
    "component",
    "collector",
    "analyzer",
    "plugin",
    "exporter",
    "serializer",
    "hook",
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
    "BaseCollector",
    "BaseAnalyzer",
    "BasePlugin",
    "BaseExporter",
    "BaseSerializer",
]