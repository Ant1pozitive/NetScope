"""
FX graph builder.

This builder converts a torch.nn.Module into a structural ModelGraph by using
torch.fx.symbolic_trace and then translating traced nodes into immutable graph
primitives.
"""

from __future__ import annotations

import importlib.util
from dataclasses import asdict
from typing import Any

from .exceptions import GraphBuildError, UnsupportedModelError
from .fx_graph_builder_config import FXGraphBuilderConfig
from .graph_edge import GraphEdge
from .graph_direction import GraphDirection
from .graph_node import GraphNode
from .model_graph import ModelGraph


class FXGraphBuilder:
    """
    Build a ModelGraph from a PyTorch module using torch.fx.
    """

    def __init__(self, config: FXGraphBuilderConfig | None = None) -> None:
        self._config = config or FXGraphBuilderConfig()

    @property
    def config(self) -> FXGraphBuilderConfig:
        """Return the builder configuration."""

        return self._config

    def build(
        self,
        model: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ModelGraph:
        """
        Build a structural graph for a model.

        If torch is unavailable or tracing fails and strict=False, the builder
        falls back to a single-node graph that describes the input model.
        """

        merged_metadata = dict(self._config.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)

        if importlib.util.find_spec("torch") is None:
            return self._fallback_graph(
                model=model,
                metadata=merged_metadata,
                reason="PyTorch is not installed.",
            )

        try:
            import torch
            from torch import fx, nn
        except Exception as exc:  # noqa: BLE001
            return self._fallback_graph(
                model=model,
                metadata=merged_metadata,
                reason=f"PyTorch import failed: {exc}",
            )

        if isinstance(model, fx.GraphModule):
            traced = model
            source_module = model
        elif isinstance(model, nn.Module):
            source_module = model
            try:
                traced = fx.symbolic_trace(
                    model,
                    concrete_args=(
                        self._config.concrete_args
                        if self._config.concrete_args
                        else None
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                return self._handle_trace_failure(
                    model=model,
                    metadata=merged_metadata,
                    error=exc,
                )
        else:
            raise UnsupportedModelError(
                "FXGraphBuilder expects a torch.nn.Module or torch.fx.GraphModule."
            )

        nodes, edges = self._build_primitives(
            graph_module=traced,
            source_module=source_module,
        )

        graph_metadata = {
            "builder": "FXGraphBuilder",
            "framework": "pytorch",
            "trace_type": type(traced).__name__,
            "config": {
                "name": self._config.name,
                "strict": self._config.strict,
                "include_module_metadata": self._config.include_module_metadata,
                "include_fx_metadata": self._config.include_fx_metadata,
                "include_operation_metadata": self._config.include_operation_metadata,
                "concrete_args": dict(self._config.concrete_args),
            },
            **merged_metadata,
        }

        return ModelGraph.from_nodes_edges(
            name=self._config.name,
            nodes=nodes,
            edges=edges,
            metadata=graph_metadata,
        )

    def _handle_trace_failure(
        self,
        *,
        model: Any,
        metadata: dict[str, Any],
        error: Exception,
    ) -> ModelGraph:
        if self._config.strict:
            raise GraphBuildError(
                f"FX tracing failed for {type(model).__name__}: {error}"
            ) from error

        return self._fallback_graph(
            model=model,
            metadata=metadata,
            reason=f"FX tracing failed: {error}",
        )

    def _fallback_graph(
        self,
        *,
        model: Any,
        metadata: dict[str, Any],
        reason: str,
    ) -> ModelGraph:
        """
        Build a minimal fallback graph when FX tracing is unavailable.
        """

        node = GraphNode(
            node_id="root",
            name=getattr(model, "__class__", type(model)).__name__,
            kind="module",
            op_type="fallback",
            module_path=f"{type(model).__module__}.{type(model).__qualname__}",
            attributes={
                "repr": self._safe_repr(model),
                "fallback_reason": reason,
            },
            metadata={
                "depth": 0,
                "builder": "FXGraphBuilder",
                **metadata,
            },
        )

        return ModelGraph.from_nodes_edges(
            name=self._config.name,
            nodes=[node],
            edges=[],
            metadata={
                "builder": "FXGraphBuilder",
                "framework": "pytorch",
                "trace_type": "fallback",
                "fallback_reason": reason,
                **metadata,
            },
        )

    def _build_primitives(
        self,
        *,
        graph_module: Any,
        source_module: Any,
    ) -> tuple[tuple[GraphNode, ...], tuple[GraphEdge, ...]]:
        """
        Translate an FX GraphModule into graph primitives.
        """

        fx_graph = graph_module.graph
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        module_index = self._index_modules(source_module)

        for order, fx_node in enumerate(fx_graph.nodes):
            node_id = fx_node.name
            input_nodes = tuple(input_node.name for input_node in fx_node.all_input_nodes)
            node_kind, op_type = self._resolve_kind_and_op(fx_node.op, fx_node.target)

            module_path = ""
            attributes: dict[str, Any] = {}
            if self._config.include_fx_metadata:
                attributes.update(
                    {
                        "fx_op": fx_node.op,
                        "fx_target": self._safe_target(fx_node.target),
                        "fx_name": fx_node.name,
                    }
                )
            if self._config.include_operation_metadata:
                attributes["operation_index"] = order

            if fx_node.op == "call_module":
                module_path = str(fx_node.target)
                module = module_index.get(module_path)
                if module is not None and self._config.include_module_metadata:
                    attributes.update(self._describe_module(module, module_path))

            if fx_node.op == "get_attr":
                module_path = str(fx_node.target)
                if self._config.include_module_metadata:
                    attributes.update(
                        {
                            "attribute_path": module_path,
                        }
                    )

            if fx_node.op == "placeholder":
                attributes.setdefault("role", "input")
            elif fx_node.op == "output":
                attributes.setdefault("role", "output")

            metadata = {
                "depth": order,
                "fx_op": fx_node.op,
            }

            node = GraphNode(
                node_id=node_id,
                name=str(fx_node.name),
                kind=node_kind,
                op_type=op_type,
                module_path=module_path,
                inputs=input_nodes,
                outputs=(),
                attributes=attributes,
                metadata=metadata,
            )
            nodes[node_id] = node

            for index, input_node in enumerate(input_nodes):
                edge_id = f"e_{input_node}_{node_id}_{index}"
                edges.append(
                    GraphEdge(
                        edge_id=edge_id,
                        source=input_node,
                        target=node_id,
                        relation="data_flow",
                        direction=GraphDirection.FORWARD,
                        metadata={
                            "fx_op": fx_node.op,
                            "fx_target": self._safe_target(fx_node.target),
                        },
                    )
                )

        outgoing: dict[str, list[str]] = {node_id: [] for node_id in nodes}
        for edge in edges:
            outgoing.setdefault(edge.source, []).append(edge.target)

        rebuilt_nodes = tuple(
            node.with_attributes(outputs=tuple(outgoing.get(node.node_id, [])))
            if "outputs" not in node.attributes
            else GraphNode(
                node_id=node.node_id,
                name=node.name,
                kind=node.kind,
                op_type=node.op_type,
                module_path=node.module_path,
                inputs=node.inputs,
                outputs=tuple(outgoing.get(node.node_id, [])),
                attributes=node.attributes,
                metadata=node.metadata,
            )
            for node in nodes.values()
        )

        return rebuilt_nodes, tuple(edges)

    def _index_modules(self, module: Any) -> dict[str, Any]:
        """
        Index named modules by module path.
        """

        modules: dict[str, Any] = {}
        if hasattr(module, "named_modules"):
            for name, submodule in module.named_modules():
                modules[name] = submodule
        return modules

    def _describe_module(self, module: Any, module_path: str) -> dict[str, Any]:
        """
        Build a module metadata descriptor.
        """

        parameters = list(getattr(module, "parameters", lambda: [])())
        buffers = list(getattr(module, "buffers", lambda: [])())

        trainable_parameters = sum(
            1 for parameter in parameters if getattr(parameter, "requires_grad", False)
        )

        return {
            "module_path": module_path,
            "module_class": type(module).__name__,
            "module_qualname": f"{type(module).__module__}.{type(module).__qualname__}",
            "parameter_count": len(parameters),
            "trainable_parameter_count": trainable_parameters,
            "buffer_count": len(buffers),
            "training": bool(getattr(module, "training", False)),
        }

    @staticmethod
    def _resolve_kind_and_op(op: str, target: Any) -> tuple[str, str]:
        """
        Map an FX node op to a graph node kind and operation type.
        """

        if op == "placeholder":
            return "input", "placeholder"
        if op == "output":
            return "output", "output"
        if op == "call_module":
            return "module", "call_module"
        if op == "get_attr":
            return "attribute", "get_attr"
        if op == "call_method":
            return "operation", str(target)
        if op == "call_function":
            return "operation", FXGraphBuilder._safe_target(target)
        return "operation", op

    @staticmethod
    def _safe_target(target: Any) -> str:
        """
        Return a stable string representation for FX targets.
        """

        if isinstance(target, str):
            return target

        module = getattr(target, "__module__", "")
        qualname = getattr(target, "__qualname__", "")
        name = getattr(target, "__name__", "")

        parts = [part for part in (module, qualname or name) if part]
        if parts:
            return ".".join(parts)

        return repr(target)

    @staticmethod
    def _safe_repr(value: Any) -> str:
        """
        Return a safe repr string with length limits.
        """

        try:
            text = repr(value)
        except Exception as exc:  # noqa: BLE001
            text = f"<repr failed: {exc.__class__.__name__}>"

        if len(text) > 512:
            return f"{text[:509]}..."
        return text


__all__ = [
    "FXGraphBuilder",
]