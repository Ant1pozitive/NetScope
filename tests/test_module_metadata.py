from __future__ import annotations

import torch.nn as nn # type: ignore

from netscope.module_metadata import ModuleMetadata


def test_module_metadata_from_module() -> None:
    module = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
    )

    metadata = ModuleMetadata.from_module(
        module,
        module_id="root",
        module_path="",
        name="Sequential",
        parent_path="",
        depth=0,
        is_root=True,
    )

    data = metadata.to_dict()

    assert data["module_id"] == "root"
    assert data["module_class"] == "Sequential"
    assert data["child_count"] == 2
    assert data["is_root"] is True
    assert data["is_leaf"] is False
    assert data["parameter_count"] > 0
    assert metadata.path == "root"
    assert metadata.qualified_name.endswith("Sequential")


def test_module_metadata_trainable_ratio() -> None:
    module = nn.Linear(4, 2, bias=True)

    metadata = ModuleMetadata.from_module(
        module,
        module_id="linear",
        module_path="encoder.linear",
        name="linear",
        parent_path="encoder",
        depth=1,
    )

    assert metadata.parameter_count >= metadata.trainable_parameter_count
    assert metadata.trainable_ratio is not None