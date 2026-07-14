"""
Layer tree builder.

This builder converts a module hierarchy into an immutable LayerTree by
walking named children recursively.
"""

from __future__ import annotations

from typing import Any

from .exceptions import LayerTreeBuildError
from .layer_tree import LayerTree
from .layer_tree_builder_config import LayerTreeBuilderConfig
from .layer_tree_node import LayerTreeNode
from .module_metadata import ModuleMetadata


class LayerTreeBuilder:
    """
    Build a LayerTree from a module hierarchy.
    """

    def __init__(self, config: LayerTreeBuilderConfig | None = None) -> None:
        self._config = config or LayerTreeBuilderConfig()

    @property
    def config(self) -> LayerTreeBuilderConfig:
        """Return the builder configuration."""

        return self._config

    def build(
        self,
        model: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> LayerTree:
        """
        Build a layer tree from a model.

        If the model does not expose a named_children() API and strict=False,
        the builder falls back to a single-node tree.
        """

        merged_metadata = dict(self._config.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)

        if self._config.include_root:
            try:
                root = self._build_node(
                    module=model,
                    module_path="",
                    name=self._module_name(model),
                    parent_path="",
                    depth=0,
                )
            except Exception as exc:  # noqa: BLE001
                if self._config.strict:
                    raise LayerTreeBuildError(
                        f"Layer tree build failed for {type(model).__name__}: {exc}"
                    ) from exc
                root = self._fallback_root(model=model, metadata=merged_metadata)
        else:
            root = self._build_children_only(
                model=model,
                metadata=merged_metadata,
            )

        return LayerTree.from_root(
            root=root,
            name=self._config.name,
            metadata={
                "builder": "LayerTreeBuilder",
                **merged_metadata,
            },
        )

    def _build_node(
        self,
        *,
        module: Any,
        module_path: str,
        name: str,
        parent_path: str,
        depth: int,
    ) -> LayerTreeNode:
        """
        Build a tree node recursively.
        """

        children: list[LayerTreeNode] = []
        named_children = getattr(module, "named_children", None)

        if callable(named_children):
            for child_name, child_module in named_children():
                child_path = (
                    f"{module_path}.{child_name}" if module_path else str(child_name)
                )
                child_node = self._build_node(
                    module=child_module,
                    module_path=child_path,
                    name=str(child_name),
                    parent_path=module_path,
                    depth=depth + 1,
                )
                children.append(child_node)

        node_metadata = (
            {"builder": "LayerTreeBuilder"}
            if self._config.include_module_metadata
            else {}
        )

        metadata = ModuleMetadata.from_module(
            module,
            module_id=module_path or "root",
            module_path=module_path,
            name=name,
            parent_path=parent_path,
            depth=depth,
            is_root=depth == 0,
            metadata=node_metadata,
        )

        return LayerTreeNode(metadata=metadata, children=tuple(children))

    def _build_children_only(
        self,
        *,
        model: Any,
        metadata: dict[str, Any],
    ) -> LayerTreeNode:
        """
        Build a tree that only uses the model as a root container.
        """

        if self._config.strict:
            raise LayerTreeBuildError(
                "LayerTreeBuilder requires a module hierarchy when include_root=False."
            )

        return self._fallback_root(model=model, metadata=metadata)

    def _fallback_root(
        self,
        *,
        model: Any,
        metadata: dict[str, Any],
    ) -> LayerTreeNode:
        """
        Build a minimal root-only tree.
        """

        root_metadata = ModuleMetadata.from_module(
            model,
            module_id="root",
            module_path="",
            name=self._module_name(model),
            parent_path="",
            depth=0,
            is_root=True,
            metadata={
                "builder": "LayerTreeBuilder",
                "fallback": True,
                **metadata,
            },
        )
        return LayerTreeNode(metadata=root_metadata, children=())

    @staticmethod
    def _module_name(module: Any) -> str:
        """
        Return a stable display name for a module.
        """

        if hasattr(module, "_get_name"):
            try:
                name = module._get_name()
                if isinstance(name, str) and name.strip():
                    return name.strip()
            except Exception:  # noqa: BLE001
                pass

        return type(module).__name__


__all__ = [
    "LayerTreeBuilder",
]