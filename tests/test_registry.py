from netscope.registry import Registry


def test_registry_register():

    registry = Registry[int]()

    registry.register("a", 1)

    assert registry.get("a") == 1


def test_registry_contains():

    registry = Registry[int]()

    registry.register("x", 5)

    assert "x" in registry


def test_registry_length():

    registry = Registry[int]()

    registry.register("a", 1)

    registry.register("b", 2)

    assert len(registry) == 2


def test_registry_unregister():

    registry = Registry[int]()

    registry.register("a", 1)

    registry.unregister("a")

    assert len(registry) == 0