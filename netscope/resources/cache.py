"""
In-memory cache utilities.

The cache is intentionally lightweight and thread-safe. It is designed for
short-lived runtime data, memoized analysis results, and intermediate state.
"""

from __future__ import annotations

from collections.abc import Callable, ItemsView, Iterator, KeysView, ValuesView
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True)
class CacheEntry(Generic[V]):
    """Single cache entry."""

    value: V
    created_at: datetime
    expires_at: datetime | None = None
    hits: int = 0

    def expired(self, now: datetime | None = None) -> bool:
        """Return whether the entry has expired."""

        if self.expires_at is None:
            return False

        current = now if now is not None else datetime.now(timezone.utc)
        return current >= self.expires_at


class Cache(Generic[K, V]):
    """
    Thread-safe in-memory cache.

    The cache supports:
    - optional TTL
    - max size limiting
    - explicit invalidation
    - lightweight statistics
    """

    def __init__(
        self,
        *,
        max_size: int = 1024,
        ttl_seconds: float | None = None,
    ) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be greater than zero.")
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero.")

        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._entries: dict[K, CacheEntry[V]] = {}
        self._lock = RLock()

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def ttl_seconds(self) -> float | None:
        return self._ttl_seconds

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _expiration(self, ttl_seconds: float | None = None) -> datetime | None:
        ttl = self._ttl_seconds if ttl_seconds is None else ttl_seconds
        if ttl is None:
            return None
        return self._now() + timedelta(seconds=ttl)

    def _prune_expired(self) -> None:
        now = self._now()
        expired = [key for key, entry in self._entries.items() if entry.expired(now)]
        for key in expired:
            self._entries.pop(key, None)

    def _ensure_capacity(self) -> None:
        while len(self._entries) > self._max_size:
            oldest_key = next(iter(self._entries))
            self._entries.pop(oldest_key, None)

    def set(self, key: K, value: V, *, ttl_seconds: float | None = None) -> None:
        """Store a value in the cache."""

        with self._lock:
            self._prune_expired()
            self._entries[key] = CacheEntry(
                value=value,
                created_at=self._now(),
                expires_at=self._expiration(ttl_seconds=ttl_seconds),
            )
            self._ensure_capacity()

    def get(self, key: K, default: V | None = None) -> V | None:
        """Return a cached value or a default."""

        with self._lock:
            self._prune_expired()
            entry = self._entries.get(key)
            if entry is None:
                return default
            entry.hits += 1
            return entry.value

    def get_or_set(self, key: K, factory: Callable[[], V]) -> V:
        """Return a value from cache or create it with factory."""

        with self._lock:
            self._prune_expired()
            entry = self._entries.get(key)
            if entry is not None:
                entry.hits += 1
                return entry.value

            value = factory()
            self._entries[key] = CacheEntry(
                value=value,
                created_at=self._now(),
                expires_at=self._expiration(),
            )
            self._ensure_capacity()
            return value

    def pop(self, key: K, default: V | None = None) -> V | None:
        """Remove and return a cached value."""

        with self._lock:
            entry = self._entries.pop(key, None)
            if entry is None:
                return default
            return entry.value

    def delete(self, key: K) -> None:
        """Remove a cached key if it exists."""

        with self._lock:
            self._entries.pop(key, None)

    def contains(self, key: K) -> bool:
        """Return whether the cache contains a key."""

        with self._lock:
            self._prune_expired()
            return key in self._entries

    def clear(self) -> None:
        """Remove all cached entries."""

        with self._lock:
            self._entries.clear()

    def keys(self) -> KeysView[K]:
        with self._lock:
            self._prune_expired()
            return self._entries.keys()

    def values(self) -> ValuesView[V]:
        with self._lock:
            self._prune_expired()
            return ValuesView({key: entry.value for key, entry in self._entries.items()})

    def items(self) -> ItemsView[K, V]:
        with self._lock:
            self._prune_expired()
            return ItemsView({key: entry.value for key, entry in self._entries.items()})

    def stats(self) -> dict[str, int | float | None]:
        """Return lightweight cache statistics."""

        with self._lock:
            self._prune_expired()
            size = len(self._entries)
            hits = sum(entry.hits for entry in self._entries.values())
            return {
                "size": size,
                "max_size": self._max_size,
                "ttl_seconds": self._ttl_seconds,
                "hits": hits,
            }

    def __contains__(self, key: object) -> bool:
        return self.contains(key) if isinstance(key, object) else False

    def __len__(self) -> int:
        with self._lock:
            self._prune_expired()
            return len(self._entries)

    def __iter__(self) -> Iterator[K]:
        with self._lock:
            self._prune_expired()
            return iter(tuple(self._entries.keys()))