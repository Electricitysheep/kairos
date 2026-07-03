"""Tests for the TTL cache and CachedDataProvider wrapper."""

from __future__ import annotations

import asyncio

import pandas as pd
import pytest

from kairos.data.cache import _MISS, TTLCache
from kairos.data.providers.base import DataProvider
from kairos.data.providers.cached import CachedDataProvider


class _FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class _RecordingProvider(DataProvider):
    """A DataProvider that counts calls and exposes a provider-specific method."""

    def __init__(self) -> None:
        self.price_calls = 0
        self.market_calls = 0
        self.health_calls = 0

    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        self.price_calls += 1
        return pd.DataFrame({"close": [1.0, 2.0]})

    async def fetch_market_data(self, token: str) -> dict:
        self.market_calls += 1
        return {"price": 100, "token": token}

    async def health_check(self) -> bool:
        self.health_calls += 1
        return True

    def search_token(self, query: str) -> str:  # provider-specific extra
        return f"found:{query}"


class TestTTLCache:
    def test_set_then_get_hit(self):
        cache = TTLCache(ttl_seconds=10)
        cache.set("k", 1)
        assert cache.get("k") == 1

    def test_miss_returns_sentinel(self):
        assert TTLCache().get("absent") is _MISS

    def test_entry_expires_after_ttl(self):
        clock = _FakeClock()
        cache = TTLCache(ttl_seconds=5, time_fn=clock)
        cache.set("k", "v")
        clock.t = 4.9
        assert cache.get("k") == "v"
        clock.t = 5.0
        assert cache.get("k") is _MISS

    def test_cached_none_is_distinct_from_miss(self):
        cache = TTLCache()
        cache.set("k", None)
        assert cache.get("k") is None

    def test_clear_and_len(self):
        cache = TTLCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2
        cache.clear()
        assert len(cache) == 0

    def test_negative_ttl_raises(self):
        with pytest.raises(ValueError):
            TTLCache(ttl_seconds=-1)


class TestCachedDataProvider:
    def test_price_data_is_cached(self):
        provider = _RecordingProvider()
        cached = CachedDataProvider(provider, ttl_seconds=60)
        df1 = asyncio.run(cached.fetch_price_data("SOL", days=30))
        df2 = asyncio.run(cached.fetch_price_data("SOL", days=30))
        assert provider.price_calls == 1
        assert df1 is df2

    def test_price_key_varies_by_days(self):
        provider = _RecordingProvider()
        cached = CachedDataProvider(provider)
        asyncio.run(cached.fetch_price_data("SOL", days=30))
        asyncio.run(cached.fetch_price_data("SOL", days=60))
        assert provider.price_calls == 2

    def test_market_data_is_cached(self):
        provider = _RecordingProvider()
        cached = CachedDataProvider(provider)
        asyncio.run(cached.fetch_market_data("SOL"))
        asyncio.run(cached.fetch_market_data("SOL"))
        assert provider.market_calls == 1

    def test_health_check_is_not_cached(self):
        provider = _RecordingProvider()
        cached = CachedDataProvider(provider)
        asyncio.run(cached.health_check())
        asyncio.run(cached.health_check())
        assert provider.health_calls == 2

    def test_invalidate_forces_refetch(self):
        provider = _RecordingProvider()
        cached = CachedDataProvider(provider)
        asyncio.run(cached.fetch_market_data("SOL"))
        cached.invalidate()
        asyncio.run(cached.fetch_market_data("SOL"))
        assert provider.market_calls == 2

    def test_expired_entry_refetches(self):
        provider = _RecordingProvider()
        cached = CachedDataProvider(provider, ttl_seconds=5)
        clock = _FakeClock()
        cached._cache._time = clock  # inject deterministic clock
        asyncio.run(cached.fetch_market_data("SOL"))
        clock.t = 10.0
        asyncio.run(cached.fetch_market_data("SOL"))
        assert provider.market_calls == 2

    def test_proxies_provider_specific_methods(self):
        cached = CachedDataProvider(_RecordingProvider())
        assert cached.search_token("sol") == "found:sol"
