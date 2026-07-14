"""
Hook handle primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .hook_kind import HookKind
from .hook_target import HookTarget


Remover = Callable[[], None]


@dataclass(slots=True)
class HookHandle:
    """
    Managed hook handle descriptor.

    The handle stores metadata about a registered hook and optionally a removal
    callback supplied by the runtime integration layer.
    """

    handle_id: str
    hook_kind: HookKind
    target: HookTarget
    callback_name: str
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    _remover: Remover | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.handle_id.strip():
            raise ValueError("handle_id cannot be empty.")
        if not self.callback_name.strip():
            raise ValueError("callback_name cannot be empty.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def target_id(self) -> str:
        """Return the target identifier."""

        return self.target.target_id

    def remove(self) -> None:
        """Remove the registered hook if a remover is attached."""

        if not self.active:
            return

        if self._remover is not None:
            self._remover()

        self.active = False

    def deactivate(self) -> None:
        """Mark the handle as inactive without calling the remover."""

        self.active = False

    def activate(self) -> None:
        """Mark the handle as active."""

        self.active = True

    def with_metadata(self, **kwargs: Any) -> HookHandle:
        """Return a copy with merged metadata."""

        merged = dict(self.metadata)
        merged.update(kwargs)
        return HookHandle(
            handle_id=self.handle_id,
            hook_kind=self.hook_kind,
            target=self.target,
            callback_name=self.callback_name,
            active=self.active,
            metadata=merged,
            _remover=self._remover,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the handle into a JSON-friendly dictionary."""

        return {
            "handle_id": self.handle_id,
            "hook_kind": self.hook_kind.value,
            "target": self.target.to_dict(),
            "callback_name": self.callback_name,
            "active": self.active,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "HookHandle",
]