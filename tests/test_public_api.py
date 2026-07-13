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
    EnvironmentDetector,
    GLOBAL_REGISTRY_MANAGER,
    GLOBAL_SESSION_MANAGER,
    PathResolver,
    Registry,
    RegistryManager,
    Session,
    SessionConfig,
    SessionManager,
    SessionState,
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
    assert ComponentIdentity is not None
    assert ComponentState is not None
    assert EnvironmentDetector is not None
    assert PathResolver is not None
    assert Cache is not None
    assert ArtifactManager is not None
    assert Workspace is not None