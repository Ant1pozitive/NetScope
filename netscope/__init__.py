"""
NetScope.

Universal diagnostics platform for neural networks.
"""

from __future__ import annotations

from ._version import __version__
from .activation_collector import ActivationCollector
from .base_collector import BaseCollector
from .collector_batch import CollectorBatch
from .collector_config import CollectorConfig
from .collector_kind import CollectorKind
from .collector_record import CollectorRecord
from .collector_result import CollectorResult
from .collector_summary import CollectorSummary
from .collector_target import CollectorTarget
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
from .exceptions import (
    GraphBuildError,
    GraphError,
    GraphValidationError,
    HookAdapterError,
    HookError,
    HookExecutionError,
    HookManagerError,
    HookRegistryError,
    InspectorError,
    LayerTreeBuildError,
    LayerTreeError,
    SnapshotBuildError,
)
from .fx_graph_builder import FXGraphBuilder
from .fx_graph_builder_config import FXGraphBuilderConfig
from .graph_direction import GraphDirection
from .graph_edge import GraphEdge
from .graph_node import GraphNode
from .graph_summary import GraphSummary
from .gradient_collector import GradientCollector
from .hook_adapter import (
    BackwardHookAdapter,
    BaseHookAdapter,
    ForwardHookAdapter,
    HookAdapterConfig,
    HookAttachmentGroup,
)
from .hook_event import HookEvent
from .hook_handle import HookHandle
from .hook_kind import HookKind
from .hook_manager import GLOBAL_HOOK_MANAGER, HookManager
from .hook_registry import HookRegistry
from .hook_result import HookResult
from .hook_target import HookTarget
from .identity import ComponentIdentity
from .inspection_result import InspectionResult
from .inspector import Inspector
from .inspector_config import InspectorConfig
from .interfaces import (
    BaseAnalyzer,
    BaseExporter,
    BasePlugin,
    BaseSerializer,
)
from .layer_tree import LayerTree
from .layer_tree_builder import LayerTreeBuilder
from .layer_tree_builder_config import LayerTreeBuilderConfig
from .layer_tree_node import LayerTreeNode
from .layer_tree_summary import LayerTreeSummary
from .lifecycle import ComponentState
from .model_graph import ModelGraph
from .module_metadata import ModuleMetadata
from .protocols import (
    AnalyzerProtocol,
    BaseCollectorProtocol,
    CollectorBatchProtocol,
    CollectorProtocol,
    CollectorRecordProtocol,
    CollectorResultProtocol,
    CollectorSummaryProtocol,
    CollectorTargetProtocol,
    Configurable,
    ExporterProtocol,
    GraphBuilderProtocol,
    GraphEdgeProtocol,
    GraphNodeProtocol,
    GraphProtocol,
    GraphSummaryProtocol,
    HookAdapterConfigProtocol,
    HookAdapterProtocol,
    HookAttachmentGroupProtocol,
    HookEventProtocol,
    HookHandleProtocol,
    HookManagerProtocol,
    HookRegistryProtocol,
    HookResultProtocol,
    HookTargetProtocol,
    InspectionResultProtocol,
    LayerTreeBuilderProtocol,
    LayerTreeNodeProtocol,
    LayerTreeProtocol,
    LayerTreeSummaryProtocol,
    LifecycleAware,
    ModuleMetadataProtocol,
    Named,
    PluginProtocol,
    Resettable,
    SafeHookWrapperProtocol,
    Serializable,
    SerializerProtocol,
    SessionProtocol,
    SnapshotBuilderProtocol,
    SnapshotProtocol,
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
from .safe_hook_wrapper import SafeHookWrapper
from .session import Session
from .session_config import SessionConfig
from .session_manager import GLOBAL_SESSION_MANAGER, SessionManager
from .session_state import SessionState
from .snapshot import Snapshot
from .snapshot_artifact import SnapshotArtifact
from .snapshot_builder import SnapshotBuilder
from .snapshot_builder_config import SnapshotBuilderConfig
from .snapshot_metadata import SnapshotMetadata
from .snapshot_summary import SnapshotSummary
from .state import GLOBAL_STATE, RuntimeState
from .weight_collector import WeightCollector

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
    "BaseCollectorProtocol",
    "CollectorTargetProtocol",
    "CollectorRecordProtocol",
    "CollectorBatchProtocol",
    "CollectorSummaryProtocol",
    "CollectorResultProtocol",
    "AnalyzerProtocol",
    "PluginProtocol",
    "ExporterProtocol",
    "SerializerProtocol",
    "SessionProtocol",
    "InspectionResultProtocol",
    "SnapshotProtocol",
    "SnapshotBuilderProtocol",
    "GraphNodeProtocol",
    "GraphEdgeProtocol",
    "GraphSummaryProtocol",
    "GraphProtocol",
    "GraphBuilderProtocol",
    "ModuleMetadataProtocol",
    "LayerTreeNodeProtocol",
    "LayerTreeSummaryProtocol",
    "LayerTreeProtocol",
    "LayerTreeBuilderProtocol",
    "HookTargetProtocol",
    "HookEventProtocol",
    "HookResultProtocol",
    "HookHandleProtocol",
    "HookRegistryProtocol",
    "HookManagerProtocol",
    "HookAdapterConfigProtocol",
    "HookAttachmentGroupProtocol",
    "HookAdapterProtocol",
    "SafeHookWrapperProtocol",
    "BaseCollector",
    "ActivationCollector",
    "GradientCollector",
    "WeightCollector",
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
    "SnapshotBuildError",
    "Snapshot",
    "SnapshotMetadata",
    "SnapshotSummary",
    "SnapshotArtifact",
    "SnapshotBuilderConfig",
    "SnapshotBuilder",
    "GraphError",
    "GraphBuildError",
    "GraphValidationError",
    "LayerTreeError",
    "LayerTreeBuildError",
    "HookError",
    "HookExecutionError",
    "HookRegistryError",
    "HookManagerError",
    "HookAdapterError",
    "HookKind",
    "HookTarget",
    "HookEvent",
    "HookResult",
    "HookHandle",
    "HookRegistry",
    "HookManager",
    "GLOBAL_HOOK_MANAGER",
    "SafeHookWrapper",
    "HookAdapterConfig",
    "HookAttachmentGroup",
    "BaseHookAdapter",
    "ForwardHookAdapter",
    "BackwardHookAdapter",
    "CollectorKind",
    "CollectorTarget",
    "CollectorRecord",
    "CollectorBatch",
    "CollectorSummary",
    "CollectorResult",
    "CollectorConfig",
    "GraphDirection",
    "GraphNode",
    "GraphEdge",
    "GraphSummary",
    "ModelGraph",
    "FXGraphBuilderConfig",
    "FXGraphBuilder",
    "ModuleMetadata",
    "LayerTreeNode",
    "LayerTreeSummary",
    "LayerTree",
    "LayerTreeBuilderConfig",
    "LayerTreeBuilder",
]