"""
Layer tree container.

The layer tree is the hierarchical structural representation of a model's
modules and submodules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .layer_tree_node import LayerTreeNode
from .layer_tree_summary import LayerTreeSummary


@dataclass(slots=True, frozen=True)
class LayerTree:
    """
    Immutable layer tree container.
    """

    tree_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "layer_tree"
    root: LayerTreeNode | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        tree_id = self.tree_id.strip()
        if not tree_id:
            raise ValueError("tree_id cannot be empty.")

        name = self.name.strip() or "layer_tree"
        object.__setattr__(self, "tree_id", tree_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "metadata", dict(self.metadata))

        if self.root is None:
            raise ValueError("root cannot be None.")

    @classmethod
    def from_root(
        cls,
        *,
        root: LayerTreeNode,
        name: str = "layer_tree",
        metadata: dict[str, Any] | None = None,
        tree_id: str | None = None,
    ) -> LayerTree:
        """
        Build a tree from an existing root node.
        """

        return cls(
            tree_id=tree_id or uuid4().hex,
            name=name,
            root=root,
            metadata={} if metadata is None else dict(metadata),
        )

    @property
    def summary(self) -> LayerTreeSummary:
        """Return tree summary statistics."""

        return LayerTreeSummary.from_root(
            tree_id=self.tree_id,
            name=self.name,
            root=self.root,
            metadata=self.metadata,
        )

    @property
    def node_count(self) -> int:
        """Return the number of nodes."""

        return self.summary.node_count

    @property
    def leaf_count(self) -> int:
        """Return the number of leaf nodes."""

        return self.summary.leaf_count

    @property
    def max_depth(self) -> int:
        """Return the maximum tree depth."""

        return self.summary.max_depth

    @property
    def root_path(self) -> str:
        """Return the root path."""

        return self.root.path

    def flatten(self) -> tuple[LayerTreeNode, ...]:
        """Return a pre-order flattened view of the tree."""

        return self.root.flatten()

    def find(self, path: str) -> LayerTreeNode | None:
        """Find a node by path."""

        return self.root.find(path)

    def paths(self) -> tuple[str, ...]:
        """Return all node paths."""

        return tuple(node.path for node in self.flatten())

    def with_metadata(self, **kwargs: Any) -> LayerTree:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the tree into a JSON-friendly dictionary."""

        return {
            "tree_id": self.tree_id,
            "name": self.name,
            "root_path": self.root_path,
            "root": self.root.to_dict(),
            "summary": self.summary.to_dict(),
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the tree into JSON text."""

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """Persist the tree as a JSON file."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path


__all__ = [
    "LayerTree",
]