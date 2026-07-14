from __future__ import annotations

import torch # type: ignore
import torch.nn as nn # type: ignore

from netscope.hook_adapter import BackwardHookAdapter, ForwardHookAdapter
from netscope.hook_manager import HookManager


def test_forward_hook_adapter_recursively_attaches_and_records() -> None:
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )

    manager = HookManager(module=model)
    adapter = ForwardHookAdapter(manager)

    def callback(module: nn.Module, inputs, output):
        return output

    group = adapter.attach(model, callback, name="forward_probe")

    assert group.handle_count == 3
    assert group.active_handle_count == 3
    assert len(manager.registry) == 3

    x = torch.randn(2, 4)
    y = model(x)

    assert y.shape == (2, 2)
    assert len(manager.history) == 3
    assert all(result.success for result in manager.history)
    assert all("adapter" in result.metadata for result in manager.history)

    detached = group.detach()
    assert detached == 3
    assert len(manager.registry) == 0


def test_backward_hook_adapter_recursively_attaches_and_records() -> None:
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 1),
    )

    manager = HookManager(module=model)
    adapter = BackwardHookAdapter(manager)

    def callback(module: nn.Module, grad_input, grad_output):
        return None

    group = adapter.attach(model, callback, name="backward_probe")

    assert group.handle_count == 3
    assert group.active_handle_count == 3

    x = torch.randn(2, 4, requires_grad=True)
    loss = model(x).sum()
    loss.backward()

    assert len(manager.history) >= 3
    assert any(result.success for result in manager.history)

    detached = group.detach()
    assert detached == 3
    assert len(manager.registry) == 0