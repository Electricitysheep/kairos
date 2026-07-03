"""A minimal in-memory TTL cache.

`KairosConfig.data_settings["cache_ttl_seconds"]` declares a cache TTL; this is
the mechanism behind it. See :class:`kairos.data.providers.cached.CachedDataProvider`
for the provider-facing wrapper that uses it.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Hashable

# Sentinel so that a genuinely cached ``None`` is distinct from a cache miss.
_MISS = object()


class TTLCache:
    """A minimal in-memory cache with a per-entry time-to-live.

    Not thread-safe — intended for single-process CLI / notebook use. The clock
    is injectable so expiry can be tested deterministically.
    """

    def __init__(
        self,
        ttl_seconds: float = 300.0,
        *,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")
        self._ttl = ttl_seconds
        self._time = time_fn
        self._store: dict[Hashable, tuple[float, Any]] = {}

    def get(self, key: Hashable) -> Any:
        """Return the cached value, or the ``_MISS`` sentinel if absent/expired."""
        item = self._store.get(key)
        if item is None:
            return _MISS
        expires_at, value = item
        if self._time() >= expires_at:
            del self._store[key]
            return _MISS
        return value

    def set(self, key: Hashable, value: Any) -> None:
        self._store[key] = (self._time() + self._ttl, value)

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
