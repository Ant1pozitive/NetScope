"""
Model graph primitives.

ModelGraph is the immutable container that holds nodes, edges, and summary
statistics for a model's structural representation.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .exceptions import GraphValidationError
from .graph_edge import GraphEdge
from .graph_node import GraphNode
from .graph_summary import GraphSummary


@dataclass(slots=True, frozen=True)
class ModelGraph:
    """
    Immutable model graph container.
    """

    graph_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "model_graph"
    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[GraphEdge, ...] = ()
    summary: GraphSummary = field(default_factory=GraphSummary)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        graph_id = self.graph_id.strip()
        name = self.name.strip() or "model_graph"

        if not graph_id:
            raise ValueError("graph_id cannot be empty.")

        object.__setattr__(self, "graph_id", graph_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "nodes", tuple(self.nodes))
        object.__setattr__(self, "edges", tuple(self.edges))
        object.__setattr__(self, "metadata", dict(self.metadata))

        self.validate()

    @classmethod
    def empty(
        cls,
        *,
        name: str = "model_graph",
        metadata: dict[str, Any] | None = None,
    ) -> ModelGraph:
        """Return an empty graph."""

        return cls(name=name, metadata={} if metadata is None else dict(metadata))

    @classmethod
    def from_nodes_edges(
        cls,
        *,
        name: str = "model_graph",
        nodes: tuple[GraphNode, ...] | list[GraphNode] = (),
        edges: tuple[GraphEdge, ...] | list[GraphEdge] = (),
        metadata: dict[str, Any] | None = None,
    ) -> ModelGraph:
        """Build a graph from nodes and edges."""

        node_tuple = tuple(nodes)
        edge_tuple = tuple(edges)
        summary = cls._build_summary(
            name=name,
            nodes=node_tuple,
            edges=edge_tuple,
            metadata={} if metadata is None else dict(metadata),
        )
        return cls(
            name=name,
            nodes=node_tuple,
            edges=edge_tuple,
            summary=summary,
            metadata={} if metadata is None else dict(metadata),
        )

    @property
    def node_count(self) -> int:
        """Return the number of nodes."""

        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Return the number of edges."""

        return len(self.edges)

    @property
    def root_nodes(self) -> tuple[GraphNode, ...]:
        """Return nodes that have no incoming edges."""

        index = self.node_index
        return tuple(
            index[node_id] for node_id in self.summary.root_nodes if node_id in index
        )

    @property
    def leaf_nodes(self) -> tuple[GraphNode, ...]:
        """Return nodes that have no outgoing edges."""

        index = self.node_index
        return tuple(
            index[node_id] for node_id in self.summary.leaf_nodes if node_id in index
        )

    @property
    def node_index(self) -> dict[str, GraphNode]:
        """Return a mapping from node IDs to nodes."""

        return {node.node_id: node for node in self.nodes}

    @property
    def edge_index(self) -> dict[str, GraphEdge]:
        """Return a mapping from edge IDs to edges."""

        return {edge.edge_id: edge for edge in self.edges}

    def iter_nodes(self) -> tuple[GraphNode, ...]:
        """Return all nodes as an ordered tuple."""

        return self.nodes

    def iter_edges(self) -> tuple[GraphEdge, ...]:
        """Return all edges as an ordered tuple."""

        return self.edges

    def has_node(self, node_id: str) -> bool:
        """Return whether a node exists."""

        normalized = node_id.strip()
        return normalized in self.node_index

    def get_node(self, node_id: str) -> GraphNode:
        """Return a node by its identifier."""

        normalized = node_id.strip()
        try:
            return self.node_index[normalized]
        except KeyError as exc:
            raise KeyError(f"Node '{normalized}' is not registered.") from exc

    def outgoing_edges(self, node_id: str) -> tuple[GraphEdge, ...]:
        """Return outgoing edges for a node."""

        normalized = node_id.strip()
        return tuple(edge for edge in self.edges if edge.source == normalized)

    def incoming_edges(self, node_id: str) -> tuple[GraphEdge, ...]:
        """Return incoming edges for a node."""

        normalized = node_id.strip()
        return tuple(edge for edge in self.edges if edge.target == normalized)

    def add_node(self, node: GraphNode) -> ModelGraph:
        """Return a copy with one additional node."""

        if self.has_node(node.node_id):
            raise GraphValidationError(f"Node '{node.node_id}' already exists.")

        return self.from_nodes_edges(
            name=self.name,
            nodes=self.nodes + (node,),
            edges=self.edges,
            metadata=dict(self.metadata),
        )

    def add_edge(self, edge: GraphEdge) -> ModelGraph:
        """Return a copy with one additional edge."""

        if edge.edge_id in self.edge_index:
            raise GraphValidationError(f"Edge '{edge.edge_id}' already exists.")

        return self.from_nodes_edges(
            name=self.name,
            nodes=self.nodes,
            edges=self.edges + (edge,),
            metadata=dict(self.metadata),
        )

    def extend_nodes(
        self,
        nodes: tuple[GraphNode, ...] | list[GraphNode],
    ) -> ModelGraph:
        """Return a copy with multiple additional nodes."""

        existing = self.node_index
        for node in nodes:
            if node.node_id in existing:
                raise GraphValidationError(f"Node '{node.node_id}' already exists.")
        return self.from_nodes_edges(
            name=self.name,
            nodes=self.nodes + tuple(nodes),
            edges=self.edges,
            metadata=dict(self.metadata),
        )

    def extend_edges(
        self,
        edges: tuple[GraphEdge, ...] | list[GraphEdge],
    ) -> ModelGraph:
        """Return a copy with multiple additional edges."""

        existing = self.edge_index
        for edge in edges:
            if edge.edge_id in existing:
                raise GraphValidationError(f"Edge '{edge.edge_id}' already exists.")
        return self.from_nodes_edges(
            name=self.name,
            nodes=self.nodes,
            edges=self.edges + tuple(edges),
            metadata=dict(self.metadata),
        )

    def with_metadata(self, **kwargs: Any) -> ModelGraph:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def rename(self, name: str) -> ModelGraph:
        """Return a copy with a different name."""

        normalized = name.strip()
        if not normalized:
            raise ValueError("name cannot be empty.")
        return replace(self, name=normalized)

    def validate(self) -> None:
        """Validate graph integrity."""

        node_ids = [node.node_id for node in self.nodes]
        edge_ids = [edge.edge_id for edge in self.edges]

        if len(node_ids) != len(set(node_ids)):
            raise GraphValidationError("Graph contains duplicate node IDs.")

        if len(edge_ids) != len(set(edge_ids)):
            raise GraphValidationError("Graph contains duplicate edge IDs.")

        if self.edges and not self.nodes:
            raise GraphValidationError("A graph with edges must contain nodes.")

        if self.nodes and self.edges:
            known_nodes = set(node_ids)
            missing_references = [
                edge
                for edge in self.edges
                if edge.source not in known_nodes or edge.target not in known_nodes
            ]
            if missing_references:
                first = missing_references[0]
                raise GraphValidationError(
                    "Graph contains edges that reference unknown nodes: "
                    f"{first.source!r} -> {first.target!r}"
                )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph into a JSON-friendly dictionary."""

        return {
            "graph_id": self.graph_id,
            "name": self.name,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "summary": self.summary.to_dict(),
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the graph into JSON."""

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """Persist the graph as a JSON file."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path

    @staticmethod
    def _build_summary(
        *,
        name: str,
        nodes: tuple[GraphNode, ...],
        edges: tuple[GraphEdge, ...],
        metadata: dict[str, Any],
    ) -> GraphSummary:
        """Compute a graph summary from nodes and edges."""

        incoming: dict[str, int] = defaultdict(int)
        outgoing: dict[str, int] = defaultdict(int)
        kind_counts: dict[str, int] = defaultdict(int)
        max_depth = 0

        for node in nodes:
            kind_counts[node.kind] += 1
            depth = node.depth
            if depth is not None:
                max_depth = max(max_depth, depth)

        for edge in edges:
            outgoing[edge.source] += 1
            incoming[edge.target] += 1

        root_nodes = tuple(
            sorted(node.node_id for node in nodes if incoming[node.node_id] == 0)
        )
        leaf_nodes = tuple(
            sorted(node.node_id for node in nodes if outgoing[node.node_id] == 0)
        )

        return GraphSummary(
            node_count=len(nodes),
            edge_count=len(edges),
            root_nodes=root_nodes,
            leaf_nodes=leaf_nodes,
            max_depth=max_depth,
            kind_counts=dict(kind_counts),
            metadata={
                "graph_name": name,
                **dict(metadata),
            },
        )


__all__ = [
    "ModelGraph",
]