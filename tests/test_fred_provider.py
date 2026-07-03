"""Tests for the FRED data provider."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from kairos.data.providers.base import DataProviderError
from kairos.data.providers.fred import FREDProvider


class _MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=MagicMock(), response=MagicMock())


def _patch_client(response):
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.get = AsyncMock(return_value=response)
    return patch("kairos.data.providers.fred.httpx.AsyncClient", return_value=client)


class TestFREDProvider:
    def test_missing_api_key_raises(self):
        provider = FREDProvider(api_key="")
        with pytest.raises(DataProviderError, match="API key"):
            asyncio.run(provider.fetch_price_data("GDP"))

    def test_fetch_price_data_parses_observations(self):
        response = _MockResponse(
            {
                "observations": [
                    {"date": "2024-01-01", "value": "100.0"},
                    {"date": "2024-01-02", "value": "."},  # missing → skipped
                    {"date": "2024-01-03", "value": "102.0"},
                ]
            }
        )
        provider = FREDProvider(api_key="key")
        with _patch_client(response):
            df = asyncio.run(provider.fetch_price_data("GDP", days=10))
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]
        assert len(df) == 2  # the "." row is dropped
        assert df["close"].iloc[-1] == 102.0

    def test_empty_observations_raises(self):
        provider = FREDProvider(api_key="key")
        with _patch_client(_MockResponse({"observations": []})):
            with pytest.raises(DataProviderError, match="No data"):
                asyncio.run(provider.fetch_price_data("GDP"))

    def test_fetch_market_data_returns_latest_price(self):
        response = _MockResponse(
            {"observations": [{"date": "2024-01-02", "value": "5.5"}]}
        )
        provider = FREDProvider(api_key="key")
        with _patch_client(response):
            data = asyncio.run(provider.fetch_market_data("DGS10"))
        assert data["price"] == 5.5
        assert data["market_cap"] is None

    def test_health_check_reflects_api_key(self):
        assert asyncio.run(FREDProvider(api_key="key").health_check()) is True
        assert asyncio.run(FREDProvider(api_key="").health_check()) is False
