"""
Hook adapters.

Adapters provide recursive and filtered attachment of forward/backward hooks
across module hierarchies, using HookManager as the runtime backend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, TYPE_CHECKING, Iterable
from uuid import uuid4

from .component import BaseComponent
from .context import ExecutionContext
from .exceptions import HookAdapterError, HookManagerError
from .hook_handle import HookHandle
from .hook_kind import HookKind
from .hook_manager import HookManager
from .hook_target import HookTarget

if TYPE_CHECKING:
    from .hook_result import HookResult


HookCallback = Callable[..., Any]
ModuleFilter = Callable[[str, Any], bool]


@dataclass(slots=True, frozen=True)
class HookAdapterConfig:
    """
    Configuration for recursive hook adapters.
    """

    name: str = "hook_adapter"
    recursive: bool = True
    include_root: bool = False
    max_depth: int | None = None
    strict: bool = False
    name_prefix: str = "hook"
    metadata: dict[str, Any] = field(default_factory=dict)
    module_filter: ModuleFilter | None = None
    include_root_name: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty.")
        if not self.name_prefix.strip():
            raise ValueError("name_prefix cannot be empty.")
        if self.max_depth is not None and self.max_depth < 0:
            raise ValueError("max_depth cannot be negative.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize the configuration into a JSON-friendly dictionary."""

        return {
            "name": self.name,
            "recursive": self.recursive,
            "include_root": self.include_root,
            "max_depth": self.max_depth,
            "strict": self.strict,
            "name_prefix": self.name_prefix,
            "metadata": dict(self.metadata),
            "include_root_name": self.include_root_name,
        }


@dataclass(slots=True)
class HookAttachmentGroup:
    """
    A detachable set of hook handles created by an adapter.
    """

    name: str
    hook_kind: HookKind
    handles: tuple[HookHandle, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    _manager: HookManager | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty.")
        object.__setattr__(self, "handles", tuple(self.handles))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def handle_count(self) -> int:
        """Return the total number of handles in the group."""

        return len(self.handles)

    @property
    def active_handle_count(self) -> int:
        """Return the number of active handles."""

        return sum(1 for handle in self.handles if handle.active)

    @property
    def handle_ids(self) -> tuple[str, ...]:
        """Return all handle IDs."""

        return tuple(handle.handle_id for handle in self.handles)

    def activate(self) -> None:
        """Mark all handles as active."""

        for handle in self.handles:
            handle.activate()

    def deactivate(self) -> None:
        """Mark all handles as inactive."""

        for handle in self.handles:
            handle.deactivate()

    def detach(self) -> int:
        """Detach all handles using the owning manager when available."""

        detached = 0

        if self._manager is None:
            for handle in self.handles:
                handle.remove()
                detached += 1
            return detached

        for handle in self.handles:
            try:
                self._manager.detach(handle.handle_id)
            except Exception:  # noqa: BLE001
                handle.remove()
            finally:
                detached += 1

        return detached

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-friendly snapshot of the group."""

        return {
            "name": self.name,
            "hook_kind": self.hook_kind.value,
            "created_at": self.created_at.isoformat(),
            "handle_count": self.handle_count,
            "active_handle_count": self.active_handle_count,
            "handle_ids": list(self.handle_ids),
            "handles": [handle.to_dict() for handle in self.handles],
            "metadata": dict(self.metadata),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the attachment group into a dictionary."""

        return self.snapshot()


class BaseHookAdapter(BaseComponent):
    """
    Base adapter that manages recursive hook attachment.
    """

    __slots__ = (
        "_manager",
        "_config",
    )

    hook_kind: HookKind = HookKind.CUSTOM

    def __init__(
        self,
        manager: HookManager,
        *,
        name: str | None = None,
        context: ExecutionContext | None = None,
        config: HookAdapterConfig | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if manager is None:
            raise HookAdapterError("manager cannot be None.")

        self._manager = manager
        self._config = config or HookAdapterConfig(name=name or self.__class__.__name__)

        base_metadata = dict(self._config.metadata)
        if metadata is not None:
            base_metadata.update(metadata)

        super().__init__(
            name=name or self._config.name,
            context=context,
            metadata=base_metadata,
        )

    @property
    def manager(self) -> HookManager:
        """Return the underlying hook manager."""

        return self._manager

    @property
    def config(self) -> HookAdapterConfig:
        """Return the adapter configuration."""

        return self._config

    def _iter_targets(self, module: Any) -> Iterable[tuple[str, Any, int]]:
        """
        Yield target modules and their structural depth.
        """

        if self._config.recursive and hasattr(module, "named_modules"):
            for module_path, submodule in module.named_modules():
                depth = 0 if module_path == "" else module_path.count(".") + 1
                if not self._config.include_root and module_path == "":
                    continue
                if self._config.max_depth is not None and depth > self._config.max_depth:
                    continue
                if self._config.module_filter is not None and not self._config.module_filter(module_path, submodule):
                    continue
                yield module_path, submodule, depth
            return

        if self._config.include_root:
            if self._config.module_filter is None or self._config.module_filter("", module):
                yield "", module, 0

    def _resolve_target_name(self, module_path: str, module: Any) -> str:
        """Return a stable target name for a module."""

        if module_path:
            return module_path

        if self._config.include_root_name and hasattr(module, "_get_name"):
            try:
                candidate = module._get_name()
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()
            except Exception:  # noqa: BLE001
                pass

        return type(module).__name__

    def _resolve_hook_name(self, module_path: str, module: Any) -> str:
        """Return a stable hook name for a module."""

        target_name = self._resolve_target_name(module_path, module)
        return f"{self._config.name_prefix}:{target_name}"

    def _build_group(
        self,
        *,
        handles: list[HookHandle],
        metadata: dict[str, Any] | None = None,
    ) -> HookAttachmentGroup:
        """Build a detachable group from handles."""

        group_metadata = dict(self._config.metadata)
        if metadata is not None:
            group_metadata.update(metadata)

        return HookAttachmentGroup(
            name=self._config.name,
            hook_kind=self.hook_kind,
            handles=tuple(handles),
            metadata=group_metadata,
            _manager=self._manager,
        )

    def _attach_one(
        self,
        *,
        module: Any,
        callback: HookCallback,
        module_path: str,
        depth: int,
        name: str | None,
        metadata: dict[str, Any] | None,
        fail_open: bool,
    ) -> HookHandle:
        """Attach a single hook using the configured hook kind."""

        resolved_target_name = self._resolve_target_name(module_path, module)
        resolved_hook_name = name or self._resolve_hook_name(module_path, module)
        resolved_target_id = module_path or resolved_target_name

        merged_metadata = dict(self._config.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)
        merged_metadata.update(
            {
                "adapter": self.__class__.__name__,
                "module_path": module_path,
                "depth": depth,
                "target_name": resolved_target_name,
            }
        )

        if self.hook_kind is HookKind.FORWARD:
            return self._manager.attach_forward(
                module,
                callback,
                name=resolved_hook_name,
                target_name=resolved_target_name,
                target_id=resolved_target_id,
                module_path=module_path or None,
                metadata=merged_metadata,
                fail_open=fail_open,
            )

        if self.hook_kind is HookKind.BACKWARD:
            return self._manager.attach_backward(
                module,
                callback,
                name=resolved_hook_name,
                target_name=resolved_target_name,
                target_id=resolved_target_id,
                module_path=module_path or None,
                metadata=merged_metadata,
                fail_open=fail_open,
            )

        if self.hook_kind is HookKind.PRE_FORWARD:
            return self._manager.attach_pre_forward(
                module,
                callback,
                name=resolved_hook_name,
                target_name=resolved_target_name,
                target_id=resolved_target_id,
                module_path=module_path or None,
                metadata=merged_metadata,
                fail_open=fail_open,
            )

        if self.hook_kind is HookKind.POST_FORWARD:
            return self._manager.attach_post_forward(
                module,
                callback,
                name=resolved_hook_name,
                target_name=resolved_target_name,
                target_id=resolved_target_id,
                module_path=module_path or None,
                metadata=merged_metadata,
                fail_open=fail_open,
            )

        return self._manager.register_custom(
            callback,
            name=resolved_hook_name,
            target=HookTarget.from_object(
                module,
                target_id=resolved_target_id,
                name=resolved_target_name,
                module_path=module_path or None,
                metadata=merged_metadata,
            ),
            metadata=merged_metadata,
            fail_open=fail_open,
        )

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-friendly snapshot of the adapter state."""

        return {
            "name": self.name,
            "uid": self.uid,
            "hook_kind": self.hook_kind.value,
            "config": self._config.to_dict(),
            "metadata": dict(self.metadata),
            "context": None if self.context is None else self.context.to_dict(),
            "manager": self._manager.snapshot(),
        }


class ForwardHookAdapter(BaseHookAdapter):
    """Recursively attach forward hooks."""

    hook_kind: HookKind = HookKind.FORWARD

    def attach(
        self,
        module: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookAttachmentGroup:
        """
        Attach a forward hook to all selected modules.
        """

        handles: list[HookHandle] = []
        for module_path, submodule, depth in self._iter_targets(module):
            try:
                handle = self._attach_one(
                    module=submodule,
                    callback=callback,
                    module_path=module_path,
                    depth=depth,
                    name=name,
                    metadata=metadata,
                    fail_open=fail_open,
                )
                handles.append(handle)
            except Exception as exc:  # noqa: BLE001
                if self.config.strict:
                    raise HookAdapterError(
                        f"Failed to attach forward hook at '{module_path or '<root>'}': {exc}"
                    ) from exc

        return self._build_group(
            handles=handles,
            metadata={
                "target_module_type": type(module).__name__,
                "attached_kind": self.hook_kind.value,
            },
        )

    def attach_to_model(
        self,
        model: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookAttachmentGroup:
        """Alias for attach()."""

        return self.attach(
            model,
            callback,
            name=name,
            metadata=metadata,
            fail_open=fail_open,
        )


class BackwardHookAdapter(BaseHookAdapter):
    """Recursively attach backward hooks."""

    hook_kind: HookKind = HookKind.BACKWARD

    def attach(
        self,
        module: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookAttachmentGroup:
        """
        Attach a backward hook to all selected modules.
        """

        handles: list[HookHandle] = []
        for module_path, submodule, depth in self._iter_targets(module):
            try:
                handle = self._attach_one(
                    module=submodule,
                    callback=callback,
                    module_path=module_path,
                    depth=depth,
                    name=name,
                    metadata=metadata,
                    fail_open=fail_open,
                )
                handles.append(handle)
            except Exception as exc:  # noqa: BLE001
                if self.config.strict:
                    raise HookAdapterError(
                        f"Failed to attach backward hook at '{module_path or '<root>'}': {exc}"
                    ) from exc

        return self._build_group(
            handles=handles,
            metadata={
                "target_module_type": type(module).__name__,
                "attached_kind": self.hook_kind.value,
            },
        )

    def attach_to_model(
        self,
        model: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookAttachmentGroup:
        """Alias for attach()."""

        return self.attach(
            model,
            callback,
            name=name,
            metadata=metadata,
            fail_open=fail_open,
        )


__all__ = [
    "HookAdapterConfig",
    "HookAttachmentGroup",
    "BaseHookAdapter",
    "ForwardHookAdapter",
    "BackwardHookAdapter",
]