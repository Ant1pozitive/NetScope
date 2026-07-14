"""
Graph node primitives.

Nodes are the smallest serializable units of a computational graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(slots=True, frozen=True)
class GraphNode:
    """
    Immutable graph node descriptor.
    """

    node_id: str
    name: str = ""
    kind: str = "module"
    op_type: str = "unknown"
    module_path: str = ""
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        node_id = self.node_id.strip()
        if not node_id:
            raise ValueError("node_id cannot be empty.")

        object.__setattr__(self, "node_id", node_id)
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "kind", self.kind.strip() or "module")
        object.__setattr__(self, "op_type", self.op_type.strip() or "unknown")
        object.__setattr__(self, "module_path", self.module_path.strip())
        object.__setattr__(
            self,
            "inputs",
            tuple(str(item).strip() for item in self.inputs if str(item).strip()),
        )
        object.__setattr__(
            self,
            "outputs",
            tuple(str(item).strip() for item in self.outputs if str(item).strip()),
        )
        object.__setattr__(self, "attributes", dict(self.attributes))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def has_inputs(self) -> bool:
        """Return whether the node has incoming references."""

        return len(self.inputs) > 0

    @property
    def has_outputs(self) -> bool:
        """Return whether the node has outgoing references."""

        return len(self.outputs) > 0

    @property
    def has_connections(self) -> bool:
        """Return whether the node has at least one connection."""

        return self.has_inputs or self.has_outputs

    @property
    def is_root(self) -> bool:
        """Return whether the node has no inputs."""

        return not self.has_inputs

    @property
    def is_leaf(self) -> bool:
        """Return whether the node has no outputs."""

        return not self.has_outputs

    @property
    def degree(self) -> int:
        """Return the total number of incident references."""

        return len(self.inputs) + len(self.outputs)

    @property
    def depth(self) -> int | None:
        """Return node depth if present in metadata."""

        value = self.metadata.get("depth")
        return value if isinstance(value, int) else None

    def with_inputs(self, inputs: tuple[str, ...] | list[str]) -> GraphNode:
        """Return a copy with updated inputs."""

        return replace(self, inputs=tuple(inputs))

    def with_outputs(self, outputs: tuple[str, ...] | list[str]) -> GraphNode:
        """Return a copy with updated outputs."""

        return replace(self, outputs=tuple(outputs))

    def with_connections(
        self,
        *,
        inputs: tuple[str, ...] | list[str] | None = None,
        outputs: tuple[str, ...] | list[str] | None = None,
    ) -> GraphNode:
        """Return a copy with updated inputs and/or outputs."""

        updated_inputs = self.inputs if inputs is None else tuple(inputs)
        updated_outputs = self.outputs if outputs is None else tuple(outputs)
        return replace(self, inputs=updated_inputs, outputs=updated_outputs)

    def with_metadata(self, **kwargs: Any) -> GraphNode:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def with_attributes(self, **kwargs: Any) -> GraphNode:
        """Return a copy with merged attributes."""

        merged = dict(self.attributes)
        merged.update(kwargs)
        return replace(self, attributes=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the node into a JSON-friendly dictionary."""

        return {
            "node_id": self.node_id,
            "name": self.name,
            "kind": self.kind,
            "op_type": self.op_type,
            "module_path": self.module_path,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "GraphNode",
]