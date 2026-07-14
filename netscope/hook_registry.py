"""
Hook registry.

This registry keeps track of hook handles and provides lookup utilities by
handle ID, target ID, and hook kind.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from .exceptions import HookRegistryError
from .hook_handle import HookHandle
from .hook_kind import HookKind


@dataclass(slots=True)
class HookRegistry:
    """
    In-memory registry for active and historical hook handles.
    """

    _handles: dict[str, HookHandle] = field(default_factory=dict)

    def register(self, handle: HookHandle, *, overwrite: bool = False) -> HookHandle:
        """
        Register a hook handle.

        Parameters
        ----------
        handle:
            Handle to register.
        overwrite:
            Replace an existing handle with the same ID.
        """

        if handle.handle_id in self._handles and not overwrite:
            raise HookRegistryError(
                f"Hook handle '{handle.handle_id}' is already registered."
            )

        self._handles[handle.handle_id] = handle
        return handle

    def get(self, handle_id: str) -> HookHandle:
        """Return a hook handle by its ID."""

        key = handle_id.strip()
        if not key:
            raise HookRegistryError("handle_id cannot be empty.")

        try:
            return self._handles[key]
        except KeyError as exc:
            raise HookRegistryError(f"Hook handle '{key}' is not registered.") from exc

    def try_get(self, handle_id: str, default: HookHandle | None = None) -> HookHandle | None:
        """Return a hook handle by ID or default."""

        key = handle_id.strip()
        if not key:
            return default
        return self._handles.get(key, default)

    def remove(self, handle_id: str) -> HookHandle:
        """Remove and return a hook handle by ID."""

        key = handle_id.strip()
        if not key:
            raise HookRegistryError("handle_id cannot be empty.")

        try:
            handle = self._handles.pop(key)
        except KeyError as exc:
            raise HookRegistryError(f"Hook handle '{key}' is not registered.") from exc

        return handle

    def contains(self, handle_id: str) -> bool:
        """Return whether the registry contains the handle."""

        key = handle_id.strip()
        return bool(key) and key in self._handles

    def by_target(self, target_id: str) -> tuple[HookHandle, ...]:
        """Return all handles attached to a given target ID."""

        key = target_id.strip()
        if not key:
            return ()
        return tuple(
            handle for handle in self._handles.values() if handle.target_id == key
        )

    def by_kind(self, hook_kind: HookKind) -> tuple[HookHandle, ...]:
        """Return all handles for a given hook kind."""

        return tuple(
            handle for handle in self._handles.values() if handle.hook_kind is hook_kind
        )

    def list(self) -> tuple[HookHandle, ...]:
        """Return all registered handles."""

        return tuple(self._handles.values())

    def active(self) -> tuple[HookHandle, ...]:
        """Return only active handles."""

        return tuple(handle for handle in self._handles.values() if handle.active)

    def clear(self) -> None:
        """Remove all handles from the registry."""

        self._handles.clear()

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-friendly registry snapshot."""

        return {
            "count": len(self._handles),
            "active_count": sum(1 for handle in self._handles.values() if handle.active),
            "handles": [handle.to_dict() for handle in self._handles.values()],
        }

    def __contains__(self, handle_id: object) -> bool:
        return isinstance(handle_id, str) and self.contains(handle_id)

    def __len__(self) -> int:
        return len(self._handles)

    def __iter__(self) -> Iterator[HookHandle]:
        return iter(self._handles.values())


__all__ = [
    "HookRegistry",
]