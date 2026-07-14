"""
Hook target primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(slots=True, frozen=True)
class HookTarget:
    """
    Immutable hook target descriptor.

    This object describes the hook target in a framework-agnostic way.
    """

    target_id: str
    name: str
    target_type: str
    module_path: str = ""
    qualname: str = ""
    repr_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        target_id = self.target_id.strip()
        name = self.name.strip()
        target_type = self.target_type.strip()

        if not target_id:
            raise ValueError("target_id cannot be empty.")
        if not name:
            raise ValueError("name cannot be empty.")
        if not target_type:
            raise ValueError("target_type cannot be empty.")

        object.__setattr__(self, "target_id", target_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "target_type", target_type)
        object.__setattr__(self, "module_path", self.module_path.strip())
        object.__setattr__(self, "qualname", self.qualname.strip())
        object.__setattr__(self, "repr_text", self.repr_text.strip())
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_object(
        cls,
        target: Any,
        *,
        target_id: str | None = None,
        name: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> HookTarget:
        """
        Build a hook target descriptor from an arbitrary object.
        """

        resolved_type = type(target)
        resolved_name = name
        if resolved_name is None or not resolved_name.strip():
            resolved_name = getattr(target, "__name__", None)
        if resolved_name is None or not isinstance(resolved_name, str) or not resolved_name.strip():
            resolved_name = getattr(target, "name", None)
        if resolved_name is None or not isinstance(resolved_name, str) or not resolved_name.strip():
            resolved_name = resolved_type.__name__

        resolved_module_path = module_path
        if resolved_module_path is None:
            resolved_module_path = f"{resolved_type.__module__}.{resolved_type.__qualname__}"

        resolved_target_id = target_id
        if resolved_target_id is None or not resolved_target_id.strip():
            resolved_target_id = resolved_name

        try:
            repr_text = repr(target)
        except Exception as exc:  # noqa: BLE001
            repr_text = f"<repr failed: {exc.__class__.__name__}>"

        if len(repr_text) > 512:
            repr_text = f"{repr_text[:509]}..."

        return cls(
            target_id=resolved_target_id,
            name=resolved_name,
            target_type=resolved_type.__name__,
            module_path=resolved_module_path,
            qualname=f"{resolved_type.__module__}.{resolved_type.__qualname__}",
            repr_text=repr_text,
            metadata={} if metadata is None else dict(metadata),
        )

    @property
    def is_module(self) -> bool:
        """Return whether the target looks like a module-like object."""

        return self.target_type in {"Module", "GraphModule"}

    def with_metadata(self, **kwargs: Any) -> HookTarget:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the target into a JSON-friendly dictionary."""

        return {
            "target_id": self.target_id,
            "name": self.name,
            "target_type": self.target_type,
            "module_path": self.module_path,
            "qualname": self.qualname,
            "repr": self.repr_text,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "HookTarget",
]