from __future__ import annotations

from netscope.hook_event import HookEvent
from netscope.hook_handle import HookHandle
from netscope.hook_kind import HookKind
from netscope.hook_manager import HookManager
from netscope.hook_registry import HookRegistry
from netscope.hook_result import HookResult
from netscope.hook_target import HookTarget
from netscope.safe_hook_wrapper import SafeHookWrapper
from netscope.protocols import (
    HookEventProtocol,
    HookHandleProtocol,
    HookManagerProtocol,
    HookRegistryProtocol,
    HookResultProtocol,
    HookTargetProtocol,
    SafeHookWrapperProtocol,
)


def test_hook_protocols_compatibility() -> None:
    def callback(x: int) -> int:
        return x

    target = HookTarget.from_object(callback)
    wrapper = SafeHookWrapper(callback=callback, hook_kind=HookKind.CUSTOM, target=target)
    event = HookEvent(hook_kind=HookKind.CUSTOM, hook_name="callback", target=target)
    result = wrapper(1)
    handle = HookHandle(
        handle_id="handle-1",
        hook_kind=HookKind.CUSTOM,
        target=target,
        callback_name="callback",
    )
    registry = HookRegistry()
    manager = HookManager()

    assert isinstance(target, HookTargetProtocol)
    assert isinstance(event, HookEventProtocol)
    assert isinstance(result, HookResultProtocol)
    assert isinstance(handle, HookHandleProtocol)
    assert isinstance(wrapper, SafeHookWrapperProtocol)
    assert isinstance(registry, HookRegistryProtocol)
    assert isinstance(manager, HookManagerProtocol)