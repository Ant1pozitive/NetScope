from __future__ import annotations

from dataclasses import dataclass

import pytest # type: ignore

from netscope.exceptions import HookExecutionError
from netscope.hook_event import HookEvent
from netscope.hook_handle import HookHandle
from netscope.hook_kind import HookKind
from netscope.hook_result import HookResult
from netscope.hook_target import HookTarget
from netscope.safe_hook_wrapper import SafeHookWrapper


def test_hook_target_from_object() -> None:
    def sample_callback() -> None:
        pass

    target = HookTarget.from_object(sample_callback)

    data = target.to_dict()

    assert data["name"] == "sample_callback"
    assert data["target_type"] == "function"
    assert data["module_path"]
    assert data["qualname"]
    assert target.is_module is False


def test_hook_event_to_dict() -> None:
    target = HookTarget.from_object(lambda x: x)  # noqa: E731
    event = HookEvent(
        hook_kind=HookKind.CUSTOM,
        hook_name="custom_hook",
        target=target,
        metadata={"suite": "hooks"},
        payload={"count": 1},
    )

    data = event.to_dict()

    assert data["hook_kind"] == "custom"
    assert data["hook_name"] == "custom_hook"
    assert data["target"]["name"]
    assert data["metadata"]["suite"] == "hooks"
    assert data["payload"]["count"] == 1


def test_safe_hook_wrapper_success() -> None:
    def callback(x: int, y: int = 0) -> int:
        return x + y

    wrapper = SafeHookWrapper(
        callback=callback,
        hook_kind=HookKind.CUSTOM,
        target=HookTarget.from_object(callback),
    )

    result = wrapper(3, y=4)

    assert isinstance(result, HookResult)
    assert result.success is True
    assert result.return_value == 7
    assert result.status == "success"
    assert result.event_id
    assert result.hook_name == "callback"

    data = result.to_dict()
    assert data["return_value"] == 7


def test_safe_hook_wrapper_fail_open() -> None:
    def callback(_: int) -> int:
        raise RuntimeError("boom")

    wrapper = SafeHookWrapper(
        callback=callback,
        hook_kind=HookKind.FORWARD,
        target=HookTarget.from_object(callback),
        fail_open=True,
    )

    result = wrapper(1)

    assert result.success is False
    assert result.error_type == "RuntimeError"
    assert result.error_message == "boom"
    assert result.status == "failed"


def test_safe_hook_wrapper_fail_closed_raises() -> None:
    def callback(_: int) -> int:
        raise RuntimeError("boom")

    wrapper = SafeHookWrapper(
        callback=callback,
        hook_kind=HookKind.FORWARD,
        target=HookTarget.from_object(callback),
        fail_open=False,
    )

    with pytest.raises(HookExecutionError):
        wrapper(1)


def test_hook_handle_lifecycle() -> None:
    target = HookTarget.from_object(lambda x: x)  # noqa: E731
    removed: list[bool] = []

    def remover() -> None:
        removed.append(True)

    handle = HookHandle(
        handle_id="h1",
        hook_kind=HookKind.FORWARD,
        target=target,
        callback_name="callback",
        metadata={"suite": "hooks"},
        _remover=remover,
    )

    assert handle.active is True
    assert handle.target_id == target.target_id

    handle.remove()

    assert handle.active is False
    assert removed == [True]

    data = handle.to_dict()
    assert data["callback_name"] == "callback"
    assert data["metadata"]["suite"] == "hooks"