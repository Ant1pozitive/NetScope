"""
Layer tree builder configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class LayerTreeBuilderConfig:
    """
    Immutable configuration for the layer tree builder.
    """

    name: str = "layer_tree"
    strict: bool = False
    include_root: bool = True
    include_module_metadata: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty.")


__all__ = [
    "LayerTreeBuilderConfig",
]