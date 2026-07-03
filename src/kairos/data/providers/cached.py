"""A caching wrapper for data providers.

Wrap any :class:`DataProvider` with :class:`CachedDataProvider` to avoid repeated
network calls for the same token within a TTL window (see
``KairosConfig.data_settings["cache_ttl_seconds"]``).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from kairos.data.cache import _MISS, TTLCache
from kairos.data.providers.base import DataProvider


class CachedDataProvider(DataProvider):
    """Wrap a :class:`DataProvider`, caching ``fetch_*`` results for a TTL.

    ``health_check`` is never cached (it must reflect live connectivity), and
    provider-specific methods (e.g. ``search_token``) are proxied through to the
    wrapped provider unchanged.
    """

    def __init__(self, provider: DataProvider, ttl_seconds: float = 300.0) -> None:
        self._provider = provider
        self._cache = TTLCache(ttl_seconds)

    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        key = ("price", token, days)
        cached = self._cache.get(key)
        if cached is not _MISS:
            return cached
        result = await self._provider.fetch_price_data(token, days)
        self._cache.set(key, result)
        return result

    async def fetch_market_data(self, token: str) -> dict:
        key = ("market", token)
        cached = self._cache.get(key)
        if cached is not _MISS:
            return cached
        result = await self._provider.fetch_market_data(token)
        self._cache.set(key, result)
        return result

    async def health_check(self) -> bool:
        return await self._provider.health_check()

    def invalidate(self) -> None:
        """Drop all cached entries (e.g. to force a refresh)."""
        self._cache.clear()

    def __getattr__(self, name: str) -> Any:
        # Proxy provider-specific methods. Guard against recursion before
        # ``_provider`` is set (e.g. during unpickling).
        if name == "_provider":
            raise AttributeError(name)
        return getattr(self._provider, name)
