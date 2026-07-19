"""
Shared protocols.

Higher-level modules should depend on protocols instead of concrete
implementations whenever possible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

from .collector_kind import CollectorKind
from .graph_direction import GraphDirection
from .hook_kind import HookKind
from .lifecycle import ComponentState
from .runtime_metric_kind import RuntimeMetricKind
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
    @property
    def collector_kind(self) -> CollectorKind: ...

    @property
    def history(self) -> tuple[Any, ...]: ...

    @property
    def last_result(self) -> Any | None: ...

    def collect(
        self,
        target: Any,
        *,
        context: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...

    def snapshot(self) -> dict[str, Any]: ...


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


@runtime_checkable
class GraphNodeProtocol(Serializable, Protocol):
    @property
    def node_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def kind(self) -> str: ...

    @property
    def op_type(self) -> str: ...

    @property
    def module_path(self) -> str: ...

    @property
    def inputs(self) -> tuple[str, ...]: ...

    @property
    def outputs(self) -> tuple[str, ...]: ...

    @property
    def metadata(self) -> dict[str, Any]: ...


@runtime_checkable
class GraphEdgeProtocol(Serializable, Protocol):
    @property
    def edge_id(self) -> str: ...

    @property
    def source(self) -> str: ...

    @property
    def target(self) -> str: ...

    @property
    def relation(self) -> str: ...

    @property
    def direction(self) -> GraphDirection: ...


@runtime_checkable
class GraphSummaryProtocol(Serializable, Protocol):
    @property
    def node_count(self) -> int: ...

    @property
    def edge_count(self) -> int: ...

    @property
    def root_count(self) -> int: ...

    @property
    def leaf_count(self) -> int: ...

    @property
    def max_depth(self) -> int: ...


@runtime_checkable
class GraphProtocol(Serializable, Protocol):
    @property
    def graph_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def nodes(self) -> tuple[Any, ...]: ...

    @property
    def edges(self) -> tuple[Any, ...]: ...

    @property
    def summary(self) -> GraphSummaryProtocol: ...

    @property
    def root_nodes(self) -> tuple[Any, ...]: ...

    @property
    def leaf_nodes(self) -> tuple[Any, ...]: ...

    def has_node(self, node_id: str) -> bool: ...

    def get_node(self, node_id: str) -> Any: ...

    def iter_nodes(self) -> tuple[Any, ...]: ...

    def iter_edges(self) -> tuple[Any, ...]: ...


@runtime_checkable
class GraphBuilderProtocol(Protocol):
    def build(self, model: Any, *, metadata: dict[str, Any] | None = None) -> Any: ...


@runtime_checkable
class ModuleMetadataProtocol(Serializable, Protocol):
    @property
    def module_id(self) -> str: ...

    @property
    def module_path(self) -> str: ...

    @property
    def module_class(self) -> str: ...

    @property
    def depth(self) -> int: ...

    @property
    def parameter_count(self) -> int: ...

    @property
    def trainable_parameter_count(self) -> int: ...

    @property
    def buffer_count(self) -> int: ...

    @property
    def child_count(self) -> int: ...

    @property
    def trainable_ratio(self) -> float | None: ...


@runtime_checkable
class LayerTreeNodeProtocol(Serializable, Protocol):
    @property
    def metadata(self) -> ModuleMetadataProtocol: ...

    @property
    def children(self) -> tuple[Any, ...]: ...

    @property
    def child_count(self) -> int: ...

    @property
    def depth(self) -> int: ...

    def find(self, path: str) -> Any: ...

    def flatten(self) -> tuple[Any, ...]: ...


@runtime_checkable
class LayerTreeSummaryProtocol(Serializable, Protocol):
    @property
    def tree_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def node_count(self) -> int: ...

    @property
    def leaf_count(self) -> int: ...

    @property
    def root_count(self) -> int: ...

    @property
    def internal_count(self) -> int: ...

    @property
    def max_depth(self) -> int: ...


@runtime_checkable
class LayerTreeProtocol(Serializable, Protocol):
    @property
    def tree_id(self) -> str: ...

    @property
    def root(self) -> Any: ...

    @property
    def summary(self) -> LayerTreeSummaryProtocol: ...

    @property
    def node_count(self) -> int: ...

    @property
    def leaf_count(self) -> int: ...

    @property
    def max_depth(self) -> int: ...

    @property
    def root_path(self) -> str: ...

    def find(self, path: str) -> Any: ...

    def flatten(self) -> tuple[Any, ...]: ...

    def paths(self) -> tuple[str, ...]: ...

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path: ...


@runtime_checkable
class LayerTreeBuilderProtocol(Protocol):
    def build(self, model: Any, *, metadata: dict[str, Any] | None = None) -> Any: ...


@runtime_checkable
class HookTargetProtocol(Serializable, Protocol):
    @property
    def target_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def target_type(self) -> str: ...

    @property
    def module_path(self) -> str: ...

    @property
    def qualname(self) -> str: ...


@runtime_checkable
class HookEventProtocol(Serializable, Protocol):
    @property
    def event_id(self) -> str: ...

    @property
    def hook_kind(self) -> HookKind: ...

    @property
    def hook_name(self) -> str: ...

    @property
    def target_id(self) -> str: ...

    @property
    def target_name(self) -> str: ...

    @property
    def phase(self) -> str: ...


@runtime_checkable
class HookResultProtocol(Serializable, Protocol):
    @property
    def result_id(self) -> str: ...

    @property
    def event_id(self) -> str: ...

    @property
    def hook_name(self) -> str: ...

    @property
    def success(self) -> bool: ...

    @property
    def status(self) -> str: ...

    @property
    def duration_seconds(self) -> float: ...


@runtime_checkable
class HookHandleProtocol(Serializable, Protocol):
    @property
    def handle_id(self) -> str: ...

    @property
    def hook_kind(self) -> HookKind: ...

    @property
    def callback_name(self) -> str: ...

    @property
    def active(self) -> bool: ...

    def remove(self) -> None: ...

    def deactivate(self) -> None: ...

    def activate(self) -> None: ...


@runtime_checkable
class HookRegistryProtocol(Serializable, Protocol):
    def register(self, handle: Any, *, overwrite: bool = False) -> Any: ...

    def get(self, handle_id: str) -> Any: ...

    def try_get(self, handle_id: str, default: Any | None = None) -> Any | None: ...

    def remove(self, handle_id: str) -> Any: ...

    def contains(self, handle_id: str) -> bool: ...

    def by_target(self, target_id: str) -> tuple[Any, ...]: ...

    def by_kind(self, hook_kind: HookKind) -> tuple[Any, ...]: ...

    def list(self) -> tuple[Any, ...]: ...

    def active(self) -> tuple[Any, ...]: ...

    def clear(self) -> None: ...

    def snapshot(self) -> dict[str, Any]: ...


@runtime_checkable
class HookManagerProtocol(ComponentProtocol, Protocol):
    @property
    def module(self) -> Any | None: ...

    @property
    def registry(self) -> HookRegistryProtocol: ...

    @property
    def history(self) -> tuple[Any, ...]: ...

    def set_module(self, module: Any) -> None: ...

    def attach_forward(
        self,
        module: Any,
        callback: Any,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> Any: ...

    def attach_pre_forward(
        self,
        module: Any,
        callback: Any,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> Any: ...

    def attach_post_forward(
        self,
        module: Any,
        callback: Any,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> Any: ...

    def attach_backward(
        self,
        module: Any,
        callback: Any,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> Any: ...

    def register_custom(
        self,
        callback: Any,
        *,
        name: str | None = None,
        target: Any | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> Any: ...

    def detach(self, handle_id: str) -> Any: ...

    def detach_all(self) -> int: ...

    def clear_history(self) -> None: ...

    def snapshot(self) -> dict[str, Any]: ...


@runtime_checkable
class HookAdapterConfigProtocol(Serializable, Protocol):
    @property
    def name(self) -> str: ...

    @property
    def recursive(self) -> bool: ...

    @property
    def include_root(self) -> bool: ...

    @property
    def max_depth(self) -> int | None: ...


@runtime_checkable
class HookAttachmentGroupProtocol(Serializable, Protocol):
    @property
    def name(self) -> str: ...

    @property
    def hook_kind(self) -> HookKind: ...

    @property
    def handles(self) -> tuple[Any, ...]: ...

    @property
    def handle_count(self) -> int: ...

    @property
    def active_handle_count(self) -> int: ...

    def activate(self) -> None: ...

    def deactivate(self) -> None: ...

    def detach(self) -> int: ...

    def snapshot(self) -> dict[str, Any]: ...


@runtime_checkable
class HookAdapterProtocol(ComponentProtocol, Protocol):
    @property
    def manager(self) -> HookManagerProtocol: ...

    @property
    def config(self) -> HookAdapterConfigProtocol: ...

    def attach(
        self,
        module: Any,
        callback: Callable[..., Any],
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookAttachmentGroupProtocol: ...


@runtime_checkable
class SafeHookWrapperProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class CollectorTargetProtocol(Serializable, Protocol):
    @property
    def target_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def target_type(self) -> str: ...

    @property
    def module_path(self) -> str: ...

    @property
    def qualname(self) -> str: ...


@runtime_checkable
class CollectorRecordProtocol(Serializable, Protocol):
    @property
    def record_id(self) -> str: ...

    @property
    def collector_kind(self) -> CollectorKind: ...

    @property
    def target_id(self) -> str: ...

    @property
    def target_name(self) -> str: ...

    @property
    def target_type(self) -> str: ...

    @property
    def success(self) -> bool: ...


@runtime_checkable
class CollectorBatchProtocol(Serializable, Protocol):
    @property
    def batch_id(self) -> str: ...

    @property
    def collector_name(self) -> str: ...

    @property
    def collector_kind(self) -> CollectorKind: ...

    @property
    def record_count(self) -> int: ...

    @property
    def success_count(self) -> int: ...

    @property
    def failure_count(self) -> int: ...


@runtime_checkable
class CollectorSummaryProtocol(Serializable, Protocol):
    @property
    def collector_name(self) -> str: ...

    @property
    def collector_kind(self) -> CollectorKind: ...

    @property
    def batch_count(self) -> int: ...

    @property
    def record_count(self) -> int: ...

    @property
    def success_rate(self) -> float | None: ...


@runtime_checkable
class CollectorResultProtocol(Serializable, Protocol):
    @property
    def result_id(self) -> str: ...

    @property
    def collector_name(self) -> str: ...

    @property
    def collector_kind(self) -> CollectorKind: ...

    @property
    def batch_count(self) -> int: ...

    @property
    def record_count(self) -> int: ...

    @property
    def summary(self) -> CollectorSummaryProtocol: ...

    def to_json(self, *, indent: int = 2) -> str: ...

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path: ...


@runtime_checkable
class BaseCollectorProtocol(ComponentProtocol, Protocol):
    @property
    def config(self) -> Any: ...

    @property
    def collector_type(self) -> CollectorKind: ...

    @property
    def history(self) -> tuple[Any, ...]: ...

    @property
    def last_result(self) -> Any | None: ...

    def collect(
        self,
        target: Any,
        *,
        context: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorResultProtocol: ...

    def snapshot(self) -> dict[str, Any]: ...


@runtime_checkable
class RuntimeMetricKindProtocol(Protocol):
    @property
    def value(self) -> str: ...


@runtime_checkable
class RuntimeMetricProtocol(Serializable, Protocol):
    @property
    def metric_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def kind(self) -> RuntimeMetricKind: ...

    @property
    def value(self) -> Any: ...

    @property
    def unit(self) -> str: ...

    @property
    def scope(self) -> str: ...

    @property
    def source(self) -> str: ...

    @property
    def is_numeric(self) -> bool: ...

    @property
    def numeric_value(self) -> float | None: ...


@runtime_checkable
class RuntimeSampleProtocol(Serializable, Protocol):
    @property
    def sample_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def kind(self) -> RuntimeMetricKind: ...

    @property
    def value(self) -> Any: ...

    @property
    def unit(self) -> str: ...

    @property
    def scope(self) -> str: ...

    @property
    def source(self) -> str: ...

    @property
    def step(self) -> int | None: ...

    @property
    def batch_index(self) -> int | None: ...

    @property
    def iteration(self) -> int | None: ...

    @property
    def is_numeric(self) -> bool: ...

    @property
    def numeric_value(self) -> float | None: ...


@runtime_checkable
class RuntimeSeriesProtocol(Serializable, Protocol):
    @property
    def series_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def kind(self) -> RuntimeMetricKind: ...

    @property
    def samples(self) -> tuple[Any, ...]: ...

    @property
    def sample_count(self) -> int: ...

    @property
    def duration_seconds(self) -> float | None: ...

    @property
    def min_numeric_value(self) -> float | None: ...

    @property
    def max_numeric_value(self) -> float | None: ...

    @property
    def mean_numeric_value(self) -> float | None: ...


@runtime_checkable
class RuntimeSnapshotProtocol(Serializable, Protocol):
    @property
    def snapshot_id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def metrics(self) -> tuple[Any, ...]: ...

    @property
    def samples(self) -> tuple[Any, ...]: ...

    @property
    def series(self) -> tuple[Any, ...]: ...

    @property
    def summary(self) -> Any: ...

    @property
    def is_completed(self) -> bool: ...

    def complete(self) -> Any: ...

    def to_json(self, *, indent: int = 2) -> str: ...

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path: ...


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
    "CollectorTargetProtocol",
    "CollectorRecordProtocol",
    "CollectorBatchProtocol",
    "CollectorSummaryProtocol",
    "CollectorResultProtocol",
    "BaseCollectorProtocol",
    "RuntimeMetricKindProtocol",
    "RuntimeMetricProtocol",
    "RuntimeSampleProtocol",
    "RuntimeSeriesProtocol",
    "RuntimeSnapshotProtocol",
]