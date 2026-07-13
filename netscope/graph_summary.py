"""
Graph summary primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(slots=True, frozen=True)
class GraphSummary:
    """
    Compact graph-level statistics.
    """

    node_count: int = 0
    edge_count: int = 0
    root_nodes: tuple[str, ...] = ()
    leaf_nodes: tuple[str, ...] = ()
    max_depth: int = 0
    kind_counts: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.node_count < 0:
            raise ValueError("node_count cannot be negative.")
        if self.edge_count < 0:
            raise ValueError("edge_count cannot be negative.")
        if self.max_depth < 0:
            raise ValueError("max_depth cannot be negative.")
        object.__setattr__(self, "root_nodes", tuple(self.root_nodes))
        object.__setattr__(self, "leaf_nodes", tuple(self.leaf_nodes))
        object.__setattr__(self, "kind_counts", dict(self.kind_counts))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def root_count(self) -> int:
        """Return the number of root nodes."""

        return len(self.root_nodes)

    @property
    def leaf_count(self) -> int:
        """Return the number of leaf nodes."""

        return len(self.leaf_nodes)

    @property
    def module_count(self) -> int:
        """Return the number of module-kind nodes."""

        return self.kind_counts.get("module", 0)

    @property
    def operation_count(self) -> int:
        """Return the number of non-module nodes."""

        return sum(
            count for kind, count in self.kind_counts.items() if kind != "module"
        )

    def with_metadata(self, **kwargs: Any) -> GraphSummary:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the summary into a JSON-friendly dictionary."""

        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "root_nodes": list(self.root_nodes),
            "leaf_nodes": list(self.leaf_nodes),
            "root_count": self.root_count,
            "leaf_count": self.leaf_count,
            "max_depth": self.max_depth,
            "kind_counts": dict(self.kind_counts),
            "module_count": self.module_count,
            "operation_count": self.operation_count,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "GraphSummary",
]