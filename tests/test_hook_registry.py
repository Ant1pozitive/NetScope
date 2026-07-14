from __future__ import annotations

from netscope.hook_handle import HookHandle
from netscope.hook_kind import HookKind
from netscope.hook_registry import HookRegistry
from netscope.hook_target import HookTarget


def test_hook_registry_register_get_remove() -> None:
    target = HookTarget.from_object(lambda x: x)  # noqa: E731
    handle = HookHandle(
        handle_id="handle-1",
        hook_kind=HookKind.FORWARD,
        target=target,
        callback_name="callback",
    )

    registry = HookRegistry()
    registry.register(handle)

    assert registry.contains("handle-1") is True
    assert registry.get("handle-1") is handle
    assert registry.by_kind(HookKind.FORWARD) == (handle,)
    assert registry.by_target(target.target_id) == (handle,)
    assert len(registry.active()) == 1

    removed = registry.remove("handle-1")
    assert removed is handle
    assert registry.contains("handle-1") is False


def test_hook_registry_snapshot() -> None:
    target = HookTarget.from_object(lambda x: x)  # noqa: E731
    handle = HookHandle(
        handle_id="handle-1",
        hook_kind=HookKind.CUSTOM,
        target=target,
        callback_name="callback",
    )

    registry = HookRegistry()
    registry.register(handle)

    snapshot = registry.snapshot()

    assert snapshot["count"] == 1
    assert snapshot["active_count"] == 1
    assert snapshot["handles"][0]["callback_name"] == "callback"