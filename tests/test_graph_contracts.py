from __future__ import annotations

import torch.nn as nn # type: ignore

from netscope.fx_graph_builder import FXGraphBuilder
from netscope.layer_tree_builder import LayerTreeBuilder
from netscope.protocols import (
    GraphProtocol,
    GraphSummaryProtocol,
    LayerTreeProtocol,
    LayerTreeSummaryProtocol,
)


def test_graph_and_layer_tree_contracts() -> None:
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )

    graph = FXGraphBuilder().build(model)
    tree = LayerTreeBuilder().build(model)

    assert isinstance(graph, GraphProtocol)
    assert isinstance(graph.summary, GraphSummaryProtocol)
    assert isinstance(tree, LayerTreeProtocol)
    assert isinstance(tree.summary, LayerTreeSummaryProtocol)