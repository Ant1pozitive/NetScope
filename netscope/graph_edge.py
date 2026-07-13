"""
Graph edge primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from .graph_direction import GraphDirection


@dataclass(slots=True, frozen=True)
class GraphEdge:
    """
    Immutable graph edge descriptor.
    """

    edge_id: str
    source: str
    target: str
    relation: str = "flow"
    direction: GraphDirection = GraphDirection.FORWARD
    weight: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        edge_id = self.edge_id.strip()
        source = self.source.strip()
        target = self.target.strip()
        relation = self.relation.strip() or "flow"

        if not edge_id:
            raise ValueError("edge_id cannot be empty.")
        if not source:
            raise ValueError("source cannot be empty.")
        if not target:
            raise ValueError("target cannot be empty.")

        object.__setattr__(self, "edge_id", edge_id)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "relation", relation)
        object.__setattr__(self, "attributes", dict(self.attributes))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def is_forward(self) -> bool:
        """Return whether the edge is forward-directed."""

        return self.direction is GraphDirection.FORWARD

    def with_metadata(self, **kwargs: Any) -> GraphEdge:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def with_attributes(self, **kwargs: Any) -> GraphEdge:
        """Return a copy with merged attributes."""

        merged = dict(self.attributes)
        merged.update(kwargs)
        return replace(self, attributes=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the edge into a JSON-friendly dictionary."""

        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "direction": self.direction.value,
            "weight": self.weight,
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "GraphEdge",
]