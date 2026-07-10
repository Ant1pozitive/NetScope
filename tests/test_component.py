from __future__ import annotations

import pytest

from netscope.component import BaseComponent
from netscope.exceptions import ComponentLifecycleError
from netscope.lifecycle import ComponentState


class DummyComponent(BaseComponent):
    def __init__(self) -> None:
        super().__init__(name="dummy")
        self.hooks: list[str] = []

    def _on_initialize(self) -> None:
        self.hooks.append("initialize")

    def _on_start(self) -> None:
        self.hooks.append("start")

    def _on_stop(self) -> None:
        self.hooks.append("stop")

    def _on_reset(self) -> None:
        self.hooks.append("reset")

    def _on_dispose(self) -> None:
        self.hooks.append("dispose")


def test_component_identity() -> None:
    component = DummyComponent()

    assert component.name == "dummy"
    assert component.namespace == "netscope"
    assert component.state == ComponentState.CREATED
    assert component.uid
    assert component.identity.qualified_name == "netscope.dummy"


def test_component_lifecycle() -> None:
    component = DummyComponent()

    component.initialize().start().stop().reset().dispose()

    assert component.state == ComponentState.DISPOSED
    assert component.hooks == [
        "initialize",
        "start",
        "stop",
        "reset",
        "dispose",
    ]


def test_invalid_transition_raises() -> None:
    component = DummyComponent()

    with pytest.raises(ComponentLifecycleError):
        component.start()


def test_configure_updates_metadata() -> None:
    component = DummyComponent()

    component.configure(alpha=1, beta="x")

    assert component.metadata["alpha"] == 1
    assert component.metadata["beta"] == "x"