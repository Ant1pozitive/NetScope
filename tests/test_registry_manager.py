from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Generator

import pytest

from netscope.registries import GLOBAL_REGISTRY_MANAGER, RegistryManager


@dataclass(slots=True)
class DummyObject:
    value: int


@pytest.fixture(autouse=True)
def clear_global_registry() -> Generator[None, None, None]:
    GLOBAL_REGISTRY_MANAGER.clear()
    yield
    GLOBAL_REGISTRY_MANAGER.clear()


def test_registry_manager_register_and_get() -> None:
    manager = RegistryManager()
    obj = DummyObject(value=7)

    manager.register("collector", "dummy", obj)

    assert manager.get("collector", "dummy") is obj
    assert manager.contains("collector", "dummy") is True
    assert manager.has_namespace("collector") is True
    assert manager.list("collector") == ("dummy",)


def test_registry_manager_snapshot() -> None:
    manager = RegistryManager()
    manager.register("plugin", "x", DummyObject(value=1))
    manager.register("plugin", "y", DummyObject(value=2))

    snapshot = manager.snapshot()

    assert snapshot["plugin"]["x"] == "DummyObject"
    assert snapshot["plugin"]["y"] == "DummyObject"


def test_registry_manager_clear_namespace() -> None:
    manager = RegistryManager()
    manager.register("analyzer", "a", DummyObject(value=1))
    manager.clear("analyzer")

    assert manager.has_namespace("analyzer") is False