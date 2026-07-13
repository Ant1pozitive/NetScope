from __future__ import annotations

from pathlib import Path

import pytest

from netscope.graph_direction import GraphDirection
from netscope.graph_edge import GraphEdge
from netscope.graph_node import GraphNode
from netscope.model_graph import ModelGraph


def test_graph_node_and_edge_to_dict() -> None:
    node = GraphNode(
        node_id="n1",
        name="input",
        kind="module",
        op_type="call_module",
        module_path="encoder.input",
        inputs=(),
        outputs=("n2",),
        attributes={"shape": [1, 2, 3]},
        metadata={"depth": 0},
    )
    edge = GraphEdge(
        edge_id="e1",
        source="n1",
        target="n2",
        relation="flow",
        direction=GraphDirection.FORWARD,
        weight=1.0,
        attributes={"dtype": "float32"},
    )

    node_data = node.to_dict()
    edge_data = edge.to_dict()

    assert node_data["node_id"] == "n1"
    assert node_data["module_path"] == "encoder.input"
    assert edge_data["source"] == "n1"
    assert edge_data["target"] == "n2"
    assert edge_data["direction"] == "forward"


def test_model_graph_summary_and_navigation(tmp_path: Path) -> None:
    node1 = GraphNode(
        node_id="n1",
        name="input",
        kind="module",
        op_type="call_module",
        module_path="encoder.input",
        outputs=("n2",),
        metadata={"depth": 0},
    )
    node2 = GraphNode(
        node_id="n2",
        name="hidden",
        kind="module",
        op_type="call_module",
        module_path="encoder.hidden",
        inputs=("n1",),
        metadata={"depth": 1},
    )
    edge = GraphEdge(
        edge_id="e1",
        source="n1",
        target="n2",
    )

    graph = ModelGraph.from_nodes_edges(
        name="demo-graph",
        nodes=[node1, node2],
        edges=[edge],
        metadata={"framework": "pytorch"},
    )

    assert graph.graph_id
    assert graph.name == "demo-graph"
    assert graph.node_count == 2
    assert graph.edge_count == 1
    assert graph.summary.node_count == 2
    assert graph.summary.edge_count == 1
    assert graph.summary.root_nodes == ("n1",)
    assert graph.summary.leaf_nodes == ("n2",)
    assert graph.summary.max_depth == 1
    assert graph.summary.module_count == 2
    assert graph.has_node("n1") is True
    assert graph.get_node("n2").name == "hidden"
    assert len(graph.outgoing_edges("n1")) == 1
    assert len(graph.incoming_edges("n2")) == 1

    saved = graph.save_json(tmp_path / "graph.json")
    assert saved.exists()
    assert '"graph_id"' in saved.read_text(encoding="utf-8")


def test_model_graph_add_helpers() -> None:
    graph = ModelGraph.empty(name="empty")

    node1 = GraphNode(node_id="n1", name="root")
    node2 = GraphNode(node_id="n2", name="leaf", inputs=("n1",))
    edge = GraphEdge(edge_id="e1", source="n1", target="n2")

    graph = graph.add_node(node1)
    graph = graph.add_node(node2)
    graph = graph.add_edge(edge)

    assert graph.node_count == 2
    assert graph.edge_count == 1
    assert graph.summary.root_nodes == ("n1",)
    assert graph.summary.leaf_nodes == ("n2",)


def test_model_graph_validation_duplicate_node_raises() -> None:
    node = GraphNode(node_id="n1", name="input")

    with pytest.raises(Exception):
        ModelGraph.from_nodes_edges(
            nodes=[node, node],
            edges=[],
        )