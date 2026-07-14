from __future__ import annotations

from pathlib import Path

import torch.nn as nn

from netscope.layer_tree_builder import LayerTreeBuilder


def test_layer_tree_builder_creates_hierarchy(tmp_path: Path) -> None:
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )

    tree = LayerTreeBuilder().build(model, metadata={"suite": "layer-tree"})

    assert tree.tree_id
    assert tree.name == "layer_tree"
    assert tree.root is not None
    assert tree.root.is_root is True
    assert tree.node_count == 4
    assert tree.leaf_count == 3
    assert tree.max_depth == 1
    assert tree.summary.root_path == "root"
    assert tree.metadata["suite"] == "layer-tree"

    flattened = tree.flatten()
    assert len(flattened) == 4
    assert tree.find("0") is not None
    assert tree.find("1") is not None
    assert tree.find("2") is not None

    saved = tree.save_json(tmp_path / "layer_tree.json")
    assert saved.exists()
    assert '"tree_id"' in saved.read_text(encoding="utf-8")


def test_layer_tree_to_dict() -> None:
    model = nn.Sequential(nn.Linear(2, 2))
    tree = LayerTreeBuilder().build(model)

    data = tree.to_dict()

    assert data["root_path"] == "root"
    assert data["summary"]["node_count"] == 2
    assert data["summary"]["leaf_count"] == 1
    assert data["root"]["metadata"]["module_class"] == "Sequential"