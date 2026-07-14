"""
Layer tree summary primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .layer_tree_node import LayerTreeNode


@dataclass(slots=True, frozen=True)
class LayerTreeSummary:
    """
    Compact statistics for a layer tree.
    """

    tree_id: str
    name: str
    node_count: int
    leaf_count: int
    max_depth: int
    root_path: str
    module_class_counts: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "module_class_counts", dict(self.module_class_counts))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def root_count(self) -> int:
        """Return the number of root nodes."""

        return 1 if self.node_count > 0 else 0

    @property
    def internal_count(self) -> int:
        """Return the number of non-leaf nodes."""

        return max(self.node_count - self.leaf_count, 0)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the summary into a JSON-friendly dictionary."""

        return {
            "tree_id": self.tree_id,
            "name": self.name,
            "node_count": self.node_count,
            "leaf_count": self.leaf_count,
            "root_count": self.root_count,
            "internal_count": self.internal_count,
            "max_depth": self.max_depth,
            "root_path": self.root_path,
            "module_class_counts": dict(self.module_class_counts),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_root(
        cls,
        *,
        tree_id: str,
        name: str,
        root: LayerTreeNode,
        metadata: dict[str, Any] | None = None,
    ) -> LayerTreeSummary:
        """
        Build summary statistics from a tree root.
        """

        nodes = root.flatten()
        leaf_count = sum(1 for node in nodes if node.is_leaf)
        max_depth = max((node.depth for node in nodes), default=0)
        module_class_counts: dict[str, int] = {}

        for node in nodes:
            module_class_counts[node.module_class] = (
                module_class_counts.get(node.module_class, 0) + 1
            )

        return cls(
            tree_id=tree_id,
            name=name,
            node_count=len(nodes),
            leaf_count=leaf_count,
            max_depth=max_depth,
            root_path=root.path,
            module_class_counts=module_class_counts,
            metadata={} if metadata is None else dict(metadata),
        )


__all__ = [
    "LayerTreeSummary",
]