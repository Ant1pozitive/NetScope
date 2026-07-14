from __future__ import annotations

import pytest # type: ignore

from netscope.graph_edge import GraphEdge
from netscope.graph_node import GraphNode
from netscope.model_graph import ModelGraph


def test_graph_rejects_unknown_edge_references() -> None:
    node = GraphNode(node_id="n1", name="root")
    edge = GraphEdge(edge_id="e1", source="n1", target="n2")

    with pytest.raises(Exception):
        ModelGraph.from_nodes_edges(
            nodes=[node],
            edges=[edge],
        )