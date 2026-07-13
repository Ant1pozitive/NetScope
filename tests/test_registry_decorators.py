from __future__ import annotations

from collections.abc import Generator

import pytest

from netscope.registries import GLOBAL_REGISTRY_MANAGER, collector, plugin


@pytest.fixture(autouse=True)
def clear_global_registry() -> Generator[None, None, None]:
    GLOBAL_REGISTRY_MANAGER.clear()
    yield
    GLOBAL_REGISTRY_MANAGER.clear()


def test_collector_decorator_registers_class() -> None:
    @collector("activation")
    class ActivationCollector:
        pass

    registered = GLOBAL_REGISTRY_MANAGER.get("collector", "activation")

    assert registered is ActivationCollector


def test_plugin_decorator_registers_function() -> None:
    @plugin("custom_plugin")
    def custom_plugin() -> str:
        return "ok"

    registered = GLOBAL_REGISTRY_MANAGER.get("plugin", "custom_plugin")

    assert registered is custom_plugin