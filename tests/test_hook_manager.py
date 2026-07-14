from __future__ import annotations

import torch # type: ignore
import torch.nn as nn # type: ignore

from netscope.hook_kind import HookKind
from netscope.hook_manager import GLOBAL_HOOK_MANAGER, HookManager
from netscope.hook_target import HookTarget


def test_hook_manager_attach_forward_and_snapshot() -> None:
    torch.manual_seed(0)

    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )
    model.eval()

    x = torch.randn(2, 4)
    expected = model(x).detach().clone()

    manager = HookManager(module=model)

    def callback(module: nn.Module, inputs, output):
        return torch.zeros_like(output)

    handle = manager.attach_forward(
        model[0],
        callback,
        name="linear_forward",
        target_name="linear_0",
        metadata={"suite": "hooks"},
    )

    y = model(x)

    assert torch.allclose(y, expected)
    assert handle.active is True
    assert handle.hook_kind is HookKind.FORWARD
    assert manager.registry.contains(handle.handle_id) is True
    assert len(manager.history) == 1
    assert manager.history[0].success is True
    assert manager.history[0].hook_name == "linear_forward"

    snapshot = manager.snapshot()
    assert snapshot["registry"]["count"] == 1
    assert snapshot["history_count"] == 1
    assert snapshot["active_handle_count"] == 1
    assert snapshot["history"][0]["status"] == "success"


def test_hook_manager_attach_backward_and_detach_all() -> None:
    model = nn.Linear(4, 2)
    manager = HookManager(module=model)

    def backward_callback(module: nn.Module, grad_input, grad_output):
        return None

    handle = manager.attach_backward(
        model,
        backward_callback,
        name="linear_backward",
        target_name="linear",
    )

    x = torch.randn(3, 4, requires_grad=True)
    loss = model(x).sum()
    loss.backward()

    assert handle.active is True
    assert manager.registry.contains(handle.handle_id) is True

    detached = manager.detach_all()
    assert detached >= 1
    assert len(manager.registry) == 0


def test_hook_manager_custom_registration() -> None:
    manager = HookManager()

    def custom_hook(value: int) -> int:
        return value + 1

    handle = manager.register_custom(
        custom_hook,
        name="increment",
        target=HookTarget.from_object(custom_hook),
        metadata={"suite": "custom"},
    )

    assert handle.hook_kind is HookKind.CUSTOM
    assert manager.registry.contains(handle.handle_id) is True
    assert handle.handle_id == manager.registry.get(handle.handle_id).handle_id


def test_global_hook_manager_exists() -> None:
    assert GLOBAL_HOOK_MANAGER is not None