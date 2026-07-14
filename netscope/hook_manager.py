"""
Hook manager.

The hook manager owns a module target, a hook registry, and the runtime
plumbing required to safely attach/remove forward and backward hooks.
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING
from uuid import uuid4

from .component import BaseComponent
from .context import ExecutionContext
from .exceptions import HookManagerError, HookRegistryError
from .hook_event import HookEvent
from .hook_handle import HookHandle
from .hook_kind import HookKind
from .hook_registry import HookRegistry
from .hook_result import HookResult
from .hook_target import HookTarget
from .safe_hook_wrapper import SafeHookWrapper

if TYPE_CHECKING:
    from .session import Session


HookCallback = Callable[..., Any]


class HookManager(BaseComponent):
    """
    Manage runtime hook registration for a model or module tree.
    """

    __slots__ = (
        "_module",
        "_registry",
        "_history",
    )

    def __init__(
        self,
        module: Any | None = None,
        *,
        name: str = "hook_manager",
        context: ExecutionContext | None = None,
        metadata: dict[str, Any] | None = None,
        registry: HookRegistry | None = None,
    ) -> None:
        super().__init__(
            name=name,
            context=context,
            metadata=metadata,
        )
        self._module = module
        self._registry = registry or HookRegistry()
        self._history: list[HookResult] = []

    @property
    def module(self) -> Any | None:
        """Return the currently attached module."""

        return self._module

    @property
    def registry(self) -> HookRegistry:
        """Return the internal hook registry."""

        return self._registry

    @property
    def history(self) -> tuple[HookResult, ...]:
        """Return hook execution history."""

        return tuple(self._history)

    @property
    def events(self) -> tuple[HookEvent, ...]:
        """Return hook events extracted from result history."""

        return tuple(result.event for result in self._history if result.event is not None)

    def set_module(self, module: Any) -> None:
        """Attach a new module to the hook manager."""

        self._module = module
        self.configure(module_type=type(module).__name__)

    def attach_forward(
        self,
        module: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookHandle:
        """Attach a forward hook to a module."""

        return self._attach(
            module=module,
            callback=callback,
            hook_kind=HookKind.FORWARD,
            name=name,
            target_name=target_name,
            target_id=target_id,
            module_path=module_path,
            metadata=metadata,
            fail_open=fail_open,
        )

    def attach_pre_forward(
        self,
        module: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookHandle:
        """Attach a forward pre-hook to a module."""

        return self._attach(
            module=module,
            callback=callback,
            hook_kind=HookKind.PRE_FORWARD,
            name=name,
            target_name=target_name,
            target_id=target_id,
            module_path=module_path,
            metadata=metadata,
            fail_open=fail_open,
        )

    def attach_post_forward(
        self,
        module: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookHandle:
        """
        Attach a post-forward hook to a module.

        In torch this maps to the standard forward hook lifecycle.
        """

        return self._attach(
            module=module,
            callback=callback,
            hook_kind=HookKind.POST_FORWARD,
            name=name,
            target_name=target_name,
            target_id=target_id,
            module_path=module_path,
            metadata=metadata,
            fail_open=fail_open,
        )

    def attach_backward(
        self,
        module: Any,
        callback: HookCallback,
        *,
        name: str | None = None,
        target_name: str | None = None,
        target_id: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookHandle:
        """Attach a backward hook to a module."""

        return self._attach(
            module=module,
            callback=callback,
            hook_kind=HookKind.BACKWARD,
            name=name,
            target_name=target_name,
            target_id=target_id,
            module_path=module_path,
            metadata=metadata,
            fail_open=fail_open,
        )

    def register_custom(
        self,
        callback: HookCallback,
        *,
        name: str | None = None,
        target: Any | None = None,
        metadata: dict[str, Any] | None = None,
        fail_open: bool = True,
    ) -> HookHandle:
        """
        Register a custom hook without binding it to a module handle.

        The handle is tracked in the registry and can be executed manually.
        """

        resolved_name = name or getattr(callback, "__name__", "custom_hook")
        target_obj = (
            HookTarget.from_object(
                callback,
                target_id=resolved_name,
                name=resolved_name,
                metadata={"kind": "custom"},
            )
            if target is None
            else (
                target
                if isinstance(target, HookTarget)
                else HookTarget.from_object(
                    target,
                    target_id=resolved_name,
                    name=resolved_name,
                    metadata={"kind": "custom"},
                )
            )
        )

        wrapper = SafeHookWrapper(
            callback=callback,
            hook_kind=HookKind.CUSTOM,
            hook_name=resolved_name,
            target=target_obj,
            fail_open=fail_open,
            metadata=metadata or {},
        )

        handle = HookHandle(
            handle_id=uuid4().hex,
            hook_kind=HookKind.CUSTOM,
            target=target_obj,
            callback_name=resolved_name,
            metadata={
                "wrapper": wrapper.to_dict(),
                **dict(metadata or {}),
            },
            _remover=None,
        )
        self.registry.register(handle)
        return handle

    def detach(self, handle_id: str) -> HookHandle:
        """Detach a hook by handle ID."""

        handle = self.registry.remove(handle_id)
        handle.remove()
        return handle

    def detach_all(self) -> int:
        """Detach all registered hooks."""

        detached = 0
        for handle in list(self.registry):
            try:
                handle.remove()
            finally:
                detached += 1
        self.registry.clear()
        return detached

    def clear_history(self) -> None:
        """Clear recorded hook execution history."""

        self._history.clear()

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-friendly snapshot of the hook manager."""

        return {
            "name": self.name,
            "uid": self.uid,
            "module_type": None if self._module is None else type(self._module).__name__,
            "registry": self.registry.snapshot(),
            "history": [result.to_dict() for result in self._history],
            "history_count": len(self._history),
            "active_handle_count": len(self.registry.active()),
            "metadata": dict(self.metadata),
            "context": None if self.context is None else self.context.to_dict(),
        }

    def dispose(self) -> HookManager:
        """Detach all hooks and dispose the manager."""

        self.detach_all()
        self.clear_history()
        return super().dispose()

    def _attach(
        self,
        *,
        module: Any,
        callback: HookCallback,
        hook_kind: HookKind,
        name: str | None,
        target_name: str | None,
        target_id: str | None,
        module_path: str | None,
        metadata: dict[str, Any] | None,
        fail_open: bool,
    ) -> HookHandle:
        """
        Internal attachment helper.
        """

        if module is None:
            raise HookManagerError("module cannot be None.")

        resolved_target_name = (
            target_name
            or module_path
            or getattr(module, "__class__", type(module)).__name__
        )
        resolved_target_id = target_id or module_path or resolved_target_name

        resolved_target = HookTarget.from_object(
            module,
            target_id=resolved_target_id,
            name=resolved_target_name,
            module_path=module_path,
            metadata={"hook_kind": hook_kind.value, **dict(metadata or {})},
        )

        wrapper = SafeHookWrapper(
            callback=callback,
            hook_kind=hook_kind,
            hook_name=name,
            target=resolved_target,
            fail_open=fail_open,
            metadata=dict(metadata or {}),
        )

        dispatch = self._build_dispatch(wrapper)

        remover = self._register_with_module(
            module=module,
            hook_kind=hook_kind,
            dispatch=dispatch,
        )

        handle = HookHandle(
            handle_id=uuid4().hex,
            hook_kind=hook_kind,
            target=resolved_target,
            callback_name=wrapper.resolved_hook_name,
            metadata=dict(metadata or {}),
            _remover=remover,
        )

        self.registry.register(handle)
        return handle

    def _build_dispatch(self, wrapper: SafeHookWrapper) -> HookCallback:
        """
        Build a runtime dispatch function that records hook results.
        """

        def dispatch(*args: Any, **kwargs: Any) -> Any:
            result = wrapper(*args, **kwargs)
            self._record(result)
            return result.return_value

        return dispatch

    def _record(self, result: HookResult) -> None:
        """
        Record hook execution results in memory.
        """

        self._history.append(result)

    def _register_with_module(
        self,
        *,
        module: Any,
        hook_kind: HookKind,
        dispatch: HookCallback,
    ) -> Callable[[], None]:
        """
        Register the dispatch function with a module object and return remover.
        """

        if hook_kind in {HookKind.FORWARD, HookKind.POST_FORWARD}:
            register = getattr(module, "register_forward_hook", None)
            if callable(register):
                handle = register(dispatch)
                return handle.remove

        if hook_kind is HookKind.PRE_FORWARD:
            register = getattr(module, "register_forward_pre_hook", None)
            if callable(register):
                handle = register(dispatch)
                return handle.remove

        if hook_kind is HookKind.BACKWARD:
            register = getattr(module, "register_full_backward_hook", None)
            if callable(register):
                handle = register(dispatch)
                return handle.remove

            register = getattr(module, "register_backward_hook", None)
            if callable(register):
                handle = register(dispatch)
                return handle.remove

        raise HookManagerError(
            f"Module of type '{type(module).__name__}' does not support hook kind '{hook_kind.value}'."
        )

    def _on_dispose(self) -> None:
        """Cleanup hooks when the manager is disposed."""

        self.detach_all()
        self.clear_history()


GLOBAL_HOOK_MANAGER = HookManager()

__all__ = [
    "HookManager",
    "GLOBAL_HOOK_MANAGER",
]