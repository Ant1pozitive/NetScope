"""
Module metadata models.

These models describe structural information about a module or layer in a
model hierarchy. They are intentionally framework-agnostic at the data level,
while the builder can extract details from PyTorch modules when available.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(slots=True, frozen=True)
class ModuleMetadata:
    """
    Immutable module descriptor used by the layer tree.
    """

    module_id: str
    module_path: str = ""
    name: str = ""
    parent_path: str = ""
    depth: int = 0
    module_class: str = "Module"
    module_qualname: str = ""
    parameter_count: int = 0
    trainable_parameter_count: int = 0
    buffer_count: int = 0
    child_count: int = 0
    training: bool | None = None
    is_root: bool = False
    is_leaf: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        module_id = self.module_id.strip()
        if not module_id:
            raise ValueError("module_id cannot be empty.")

        object.__setattr__(self, "module_id", module_id)
        object.__setattr__(self, "module_path", self.module_path.strip())
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "parent_path", self.parent_path.strip())
        object.__setattr__(self, "module_class", self.module_class.strip() or "Module")
        object.__setattr__(self, "module_qualname", self.module_qualname.strip())
        object.__setattr__(self, "parameter_count", int(self.parameter_count))
        object.__setattr__(
            self,
            "trainable_parameter_count",
            int(self.trainable_parameter_count),
        )
        object.__setattr__(self, "buffer_count", int(self.buffer_count))
        object.__setattr__(self, "child_count", int(self.child_count))
        object.__setattr__(self, "depth", int(self.depth))
        object.__setattr__(self, "metadata", dict(self.metadata))

        if self.child_count < 0:
            raise ValueError("child_count cannot be negative.")
        if self.depth < 0:
            raise ValueError("depth cannot be negative.")

    @classmethod
    def from_module(
        cls,
        module: Any,
        *,
        module_id: str,
        module_path: str = "",
        name: str = "",
        parent_path: str = "",
        depth: int = 0,
        is_root: bool | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ModuleMetadata:
        """
        Build metadata from a module-like object.
        """

        module_class = type(module).__name__
        module_qualname = f"{type(module).__module__}.{type(module).__qualname__}"
        child_count = cls._count_children(module)
        parameter_count = cls._count_parameters(module, recurse=True)
        trainable_parameter_count = cls._count_trainable_parameters(module, recurse=True)
        buffer_count = cls._count_buffers(module, recurse=True)
        training = cls._safe_training_flag(module)

        if not name.strip():
            name = module_path.split(".")[-1] if module_path else module_class

        if is_root is None:
            is_root = depth == 0

        return cls(
            module_id=module_id,
            module_path=module_path,
            name=name,
            parent_path=parent_path,
            depth=depth,
            module_class=module_class,
            module_qualname=module_qualname,
            parameter_count=parameter_count,
            trainable_parameter_count=trainable_parameter_count,
            buffer_count=buffer_count,
            child_count=child_count,
            training=training,
            is_root=is_root,
            is_leaf=child_count == 0,
            metadata={} if metadata is None else dict(metadata),
        )

    @staticmethod
    def _safe_training_flag(module: Any) -> bool | None:
        training = getattr(module, "training", None)
        return training if isinstance(training, bool) else None

    @staticmethod
    def _count_children(module: Any) -> int:
        named_children = getattr(module, "named_children", None)
        if not callable(named_children):
            return 0
        try:
            return sum(1 for _ in named_children())
        except Exception:  # noqa: BLE001
            return 0

    @staticmethod
    def _count_parameters(module: Any, *, recurse: bool) -> int:
        provider = getattr(module, "parameters", None)
        if not callable(provider):
            return 0
        try:
            items = provider(recurse=recurse)
        except TypeError:
            try:
                items = provider()
            except Exception:  # noqa: BLE001
                return 0
        except Exception:  # noqa: BLE001
            return 0
        return sum(1 for _ in items)

    @staticmethod
    def _count_trainable_parameters(module: Any, *, recurse: bool) -> int:
        provider = getattr(module, "parameters", None)
        if not callable(provider):
            return 0
        try:
            items = provider(recurse=recurse)
        except TypeError:
            try:
                items = provider()
            except Exception:  # noqa: BLE001
                return 0
        except Exception:  # noqa: BLE001
            return 0
        return sum(
            1 for parameter in items if getattr(parameter, "requires_grad", False)
        )

    @staticmethod
    def _count_buffers(module: Any, *, recurse: bool) -> int:
        provider = getattr(module, "buffers", None)
        if not callable(provider):
            return 0
        try:
            items = provider(recurse=recurse)
        except TypeError:
            try:
                items = provider()
            except Exception:  # noqa: BLE001
                return 0
        except Exception:  # noqa: BLE001
            return 0
        return sum(1 for _ in items)

    @property
    def path(self) -> str:
        """Return the canonical path for the module."""

        return self.module_path or self.module_id

    @property
    def qualified_name(self) -> str:
        """Return the fully qualified module class name."""

        return self.module_qualname or self.module_class

    @property
    def has_children(self) -> bool:
        """Return whether the module has children."""

        return self.child_count > 0

    @property
    def has_parameters(self) -> bool:
        """Return whether the module has parameters."""

        return self.parameter_count > 0

    @property
    def trainable_ratio(self) -> float | None:
        """Return trainable parameter ratio if available."""

        if self.parameter_count <= 0:
            return None
        return self.trainable_parameter_count / self.parameter_count

    def with_metadata(self, **kwargs: Any) -> ModuleMetadata:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the metadata into a JSON-friendly dictionary."""

        return {
            "module_id": self.module_id,
            "module_path": self.module_path,
            "path": self.path,
            "name": self.name,
            "parent_path": self.parent_path,
            "depth": self.depth,
            "module_class": self.module_class,
            "module_qualname": self.module_qualname,
            "parameter_count": self.parameter_count,
            "trainable_parameter_count": self.trainable_parameter_count,
            "buffer_count": self.buffer_count,
            "child_count": self.child_count,
            "training": self.training,
            "is_root": self.is_root,
            "is_leaf": self.is_leaf,
            "trainable_ratio": self.trainable_ratio,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "ModuleMetadata",
]