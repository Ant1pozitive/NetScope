from __future__ import annotations

from netscope import (
    ArtifactManager,
    BaseAnalyzer,
    BaseCollector,
    BaseComponent,
    BaseExporter,
    BasePlugin,
    BaseSerializer,
    Cache,
    ComponentIdentity,
    ComponentState,
    DeviceResolver,
    EnvironmentDetector,
    FXGraphBuilder,
    FXGraphBuilderConfig,
    GLOBAL_REGISTRY_MANAGER,
    GLOBAL_SESSION_MANAGER,
    GraphBuildError,
    GraphDirection,
    GraphEdge,
    GraphEdgeProtocol,
    GraphError,
    GraphNode,
    GraphNodeProtocol,
    GraphProtocol,
    GraphSummary,
    GraphSummaryProtocol,
    GraphValidationError,
    InspectionResult,
    InspectionResultProtocol,
    Inspector,
    InspectorConfig,
    LayerTree,
    LayerTreeBuildError,
    LayerTreeBuilder,
    LayerTreeBuilderConfig,
    LayerTreeBuilderProtocol,
    LayerTreeError,
    LayerTreeNode,
    LayerTreeNodeProtocol,
    LayerTreeProtocol,
    LayerTreeSummary,
    LayerTreeSummaryProtocol,
    ModelGraph,
    ModuleMetadata,
    ModuleMetadataProtocol,
    PathResolver,
    Registry,
    RegistryManager,
    Session,
    SessionConfig,
    SessionManager,
    SessionProtocol,
    SessionState,
    Snapshot,
    SnapshotArtifact,
    SnapshotBuilder,
    SnapshotBuilderConfig,
    SnapshotBuilderProtocol,
    SnapshotMetadata,
    SnapshotProtocol,
    SnapshotSummary,
    Workspace,
    __version__,
)


def test_public_api_exports() -> None:
    assert __version__
    assert BaseComponent is not None
    assert BaseCollector is not None
    assert BaseAnalyzer is not None
    assert BasePlugin is not None
    assert BaseExporter is not None
    assert BaseSerializer is not None
    assert Registry is not None
    assert RegistryManager is not None
    assert GLOBAL_REGISTRY_MANAGER is not None
    assert GLOBAL_SESSION_MANAGER is not None
    assert Session is not None
    assert SessionConfig is not None
    assert SessionManager is not None
    assert SessionState is not None
    assert SessionProtocol is not None
    assert Inspector is not None
    assert InspectorConfig is not None
    assert InspectionResult is not None
    assert InspectionResultProtocol is not None
    assert Snapshot is not None
    assert SnapshotProtocol is not None
    assert SnapshotMetadata is not None
    assert SnapshotSummary is not None
    assert SnapshotArtifact is not None
    assert SnapshotBuilder is not None
    assert SnapshotBuilderConfig is not None
    assert SnapshotBuilderProtocol is not None
    assert ComponentIdentity is not None
    assert ComponentState is not None
    assert EnvironmentDetector is not None
    assert DeviceResolver is not None
    assert PathResolver is not None
    assert Cache is not None
    assert ArtifactManager is not None
    assert Workspace is not None
    assert GraphError is not None
    assert GraphBuildError is not None
    assert GraphValidationError is not None
    assert GraphDirection is not None
    assert GraphNode is not None
    assert GraphEdge is not None
    assert GraphSummary is not None
    assert ModelGraph is not None
    assert FXGraphBuilder is not None
    assert FXGraphBuilderConfig is not None
    assert GraphNodeProtocol is not None
    assert GraphEdgeProtocol is not None
    assert GraphSummaryProtocol is not None
    assert GraphProtocol is not None
    assert ModuleMetadata is not None
    assert ModuleMetadataProtocol is not None
    assert LayerTreeNode is not None
    assert LayerTreeNodeProtocol is not None
    assert LayerTreeSummary is not None
    assert LayerTreeSummaryProtocol is not None
    assert LayerTree is not None
    assert LayerTreeProtocol is not None
    assert LayerTreeBuilder is not None
    assert LayerTreeBuilderConfig is not None
    assert LayerTreeBuilderProtocol is not None
    assert LayerTreeError is not None
    assert LayerTreeBuildError is not None