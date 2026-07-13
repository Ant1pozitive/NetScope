"""
NetScope.

Universal diagnostics platform for neural networks.
"""

from __future__ import annotations

from ._version import __version__
from .component import BaseComponent
from .config import CONFIG
from .context import ExecutionContext
from .environment import (
    DeviceResolver,
    Environment,
    EnvironmentDetector,
    PlatformInfo,
    TorchInfo,
    VersionInfo,
)
from .exceptions import InspectorError
from .identity import ComponentIdentity
from .inspection_result import InspectionResult
from .inspector import Inspector
from .inspector_config import InspectorConfig
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
    SessionProtocol,
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
from .resources import ArtifactManager, Cache, PathResolver, TempDirectory, Workspace
from .session import Session
from .session_config import SessionConfig
from .session_manager import GLOBAL_SESSION_MANAGER, SessionManager
from .session_state import SessionState
from .state import GLOBAL_STATE, RuntimeState

__all__ = [
    "__version__",
    "CONFIG",
    "GLOBAL_STATE",
    "RuntimeState",
    "ExecutionContext",
    "Environment",
    "EnvironmentDetector",
    "PlatformInfo",
    "TorchInfo",
    "VersionInfo",
    "DeviceResolver",
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
    "SessionProtocol",
    "BaseCollector",
    "BaseAnalyzer",
    "BasePlugin",
    "BaseExporter",
    "BaseSerializer",
    "PathResolver",
    "TempDirectory",
    "Cache",
    "ArtifactManager",
    "Workspace",
    "SessionConfig",
    "SessionState",
    "Session",
    "SessionManager",
    "GLOBAL_SESSION_MANAGER",
    "InspectorConfig",
    "InspectionResult",
    "Inspector",
    "InspectorError",
]