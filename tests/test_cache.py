from __future__ import annotations

from netscope.resources import Cache


def test_cache_set_get() -> None:
    cache = Cache[str, int](max_size=10)

    cache.set("a", 1)

    assert cache.get("a") == 1
    assert "a" in cache
    assert len(cache) == 1


def test_cache_get_or_set() -> None:
    cache = Cache[str, int](max_size=10)

    value = cache.get_or_set("a", lambda: 5)

    assert value == 5
    assert cache.get("a") == 5


def test_cache_delete_and_clear() -> None:
    cache = Cache[str, int](max_size=10)

    cache.set("a", 1)
    cache.delete("a")

    assert cache.get("a") is None

    cache.set("b", 2)
    cache.clear()

    assert len(cache) == 0