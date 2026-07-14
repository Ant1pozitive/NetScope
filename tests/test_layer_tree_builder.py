from __future__ import annotations

from pathlib import Path

import torch.nn as nn # type: ignore

from netscope.layer_tree_builder import LayerTreeBuilder
from netscope.layer_tree_builder_config import LayerTreeBuilderConfig


def test_layer_tree_builder_root_only_fallback(tmp_path: Path) -> None:
    builder = LayerTreeBuilder(
        LayerTreeBuilderConfig(
            include_root=True,
            strict=False,
            metadata={"builder_suite": "fallback"},
        )
    )

    tree = builder.build(model={"not": "a module"})  # type: ignore[arg-type]

    assert tree.node_count == 1
    assert tree.leaf_count == 1
    assert tree.root.metadata.metadata["fallback"] is True
    assert tree.metadata["builder_suite"] == "fallback"


def test_layer_tree_builder_module_metadata_in_nodes() -> None:
    model = nn.Sequential(
        nn.Linear(3, 4),
        nn.ReLU(),
    )

    tree = LayerTreeBuilder().build(model)

    linear_node = tree.find("0")
    assert linear_node is not None
    assert linear_node.metadata.module_class == "Linear"
    assert linear_node.metadata.parameter_count > 0
    assert linear_node.metadata.training is True