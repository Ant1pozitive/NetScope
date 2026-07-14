"""
Layer tree node primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from .module_metadata import ModuleMetadata


@dataclass(slots=True, frozen=True)
class LayerTreeNode:
    """
    Immutable tree node describing a module and its children.
    """

    metadata: ModuleMetadata
    children: tuple[LayerTreeNode, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "children", tuple(self.children))
        object.__setattr__(self, "attributes", dict(self.attributes))

    @property
    def node_id(self) -> str:
        """Return the node identifier."""

        return self.metadata.module_id

    @property
    def path(self) -> str:
        """Return the node path."""

        return self.metadata.path

    @property
    def name(self) -> str:
        """Return the node name."""

        return self.metadata.name or self.metadata.module_class

    @property
    def module_class(self) -> str:
        """Return the module class name."""

        return self.metadata.module_class

    @property
    def depth(self) -> int:
        """Return the node depth."""

        return self.metadata.depth

    @property
    def is_root(self) -> bool:
        """Return whether the node is the tree root."""

        return self.metadata.is_root

    @property
    def is_leaf(self) -> bool:
        """Return whether the node is a leaf."""

        return len(self.children) == 0

    @property
    def child_count(self) -> int:
        """Return the number of direct children."""

        return len(self.children)

    def with_children(self, children: tuple[LayerTreeNode, ...] | list[LayerTreeNode]) -> LayerTreeNode:
        """Return a copy with new children."""

        return replace(self, children=tuple(children))

    def with_attributes(self, **kwargs: Any) -> LayerTreeNode:
        """Return a copy with merged attributes."""

        merged = dict(self.attributes)
        merged.update(kwargs)
        return replace(self, attributes=merged)

    def find(self, path: str) -> LayerTreeNode | None:
        """
        Find a node by path or node ID.
        """

        normalized = path.strip()
        if not normalized:
            return None

        if normalized in {self.node_id, self.path}:
            return self

        for child in self.children:
            found = child.find(normalized)
            if found is not None:
                return found

        return None

    def flatten(self) -> tuple[LayerTreeNode, ...]:
        """
        Return a pre-order flattened view of the subtree.
        """

        nodes = [self]
        for child in self.children:
            nodes.extend(child.flatten())
        return tuple(nodes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the node into a JSON-friendly dictionary."""

        return {
            "metadata": self.metadata.to_dict(),
            "attributes": dict(self.attributes),
            "children": [child.to_dict() for child in self.children],
        }


__all__ = [
    "LayerTreeNode",
]