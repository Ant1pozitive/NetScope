from __future__ import annotations

from pathlib import Path

import torch.nn as nn # type: ignore

from netscope.fx_graph_builder import FXGraphBuilder
from netscope.fx_graph_builder_config import FXGraphBuilderConfig
from netscope.graph_direction import GraphDirection


def test_fx_graph_builder_builds_model_graph() -> None:
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )

    graph = FXGraphBuilder().build(model, metadata={"suite": "fx"})

    assert graph.name == "fx_graph"
    assert graph.graph_id
    assert graph.node_count >= 4
    assert graph.edge_count >= 3
    assert graph.summary.node_count == graph.node_count
    assert graph.summary.edge_count == graph.edge_count
    assert graph.summary.root_count >= 1
    assert graph.summary.leaf_count >= 1
    assert graph.metadata["suite"] == "fx"
    assert graph.metadata["builder"] == "FXGraphBuilder"

    node_kinds = {node.kind for node in graph.nodes}
    assert "input" in node_kinds
    assert "module" in node_kinds
    assert "output" in node_kinds

    assert all(edge.direction is GraphDirection.FORWARD for edge in graph.edges)
    assert all(isinstance(node.outputs, tuple) for node in graph.nodes)
    assert any(node.has_outputs for node in graph.root_nodes)

    saved = graph.save_json(Path.cwd() / "tmp_fx_graph.json")
    assert saved.exists()


def test_fx_graph_builder_includes_module_metadata() -> None:
    model = nn.Sequential(
        nn.Linear(2, 3),
        nn.ReLU(),
    )

    graph = FXGraphBuilder(
        FXGraphBuilderConfig(include_module_metadata=True)
    ).build(model)

    module_nodes = [node for node in graph.nodes if node.kind == "module"]
    assert module_nodes
    assert any("parameter_count" in node.attributes for node in module_nodes)


def test_fx_graph_builder_fallback_for_non_module_when_strict_false() -> None:
    builder = FXGraphBuilder(FXGraphBuilderConfig(strict=False))
    graph = builder.build(model={"not": "a module"})  # type: ignore[arg-type]

    assert graph.node_count == 1
    assert graph.edge_count == 0
    assert graph.summary.root_count == 1
    assert graph.summary.leaf_count == 1
    assert graph.metadata["trace_type"] == "fallback"