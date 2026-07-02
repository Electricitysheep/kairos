"""Tests for CoinGeckoProvider."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from kairos.data.providers.base import DataProviderError
from kairos.data.providers.coingecko import CoinGeckoProvider


def make_mock_response(status_code: int, json_data) -> MagicMock:
    """Create a mock httpx.Response."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock._json = json_data
    mock.json.return_value = json_data
    mock.text = "mock text"
    mock.url = "http://test"
    return mock


class TestCoinGeckoProvider:
    """Test suite for CoinGeckoProvider."""

    @pytest_asyncio.fixture
    async def provider(self) -> CoinGeckoProvider:
        """Create provider instance without API key (free tier)."""
        return CoinGeckoProvider()

    @pytest_asyncio.fixture
    async def provider_with_key(self) -> CoinGeckoProvider:
        """Create provider instance with API key."""
        return CoinGeckoProvider(api_key="test-api-key")

    # ========================================================================
    # Initialization tests
    # ========================================================================

    def test_init_without_api_key(self):
        """Provider works without API key (free tier)."""
        provider = CoinGeckoProvider()
        assert provider.api_key == ""
        assert provider.BASE_URL == "https://api.coingecko.com/api/v3"

    def test_init_with_api_key(self):
        """Provider accepts API key."""
        provider = CoinGeckoProvider(api_key="my-secret-key")
        assert provider.api_key == "my-secret-key"

    # ========================================================================
    # fetch_price_data tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_fetch_price_data_returns_dataframe(self, provider: CoinGeckoProvider):
        """fetch_price_data returns DataFrame with correct columns."""
        mock_data = [
            [1700000000000, 100.0, 110.0, 95.0, 105.0],
            [1700001000000, 105.0, 115.0, 100.0, 108.0],
            [1700002000000, 108.0, 112.0, 105.0, 110.0],
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, mock_data))

            result = await provider.fetch_price_data("solana", days=30)

        assert isinstance(result, type(result))
        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns

    @pytest.mark.asyncio
    async def test_fetch_price_data_sets_volume_to_zero(self, provider: CoinGeckoProvider):
        """fetch_price_data sets volume to 0 since CoinGecko OHLC doesn't include it."""
        mock_data = [
            [1700000000000, 100.0, 110.0, 95.0, 105.0],
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, mock_data))

            result = await provider.fetch_price_data("solana")

        assert result["volume"].iloc[0] == 0

    @pytest.mark.asyncio
    async def test_fetch_price_data_empty_response(self, provider: CoinGeckoProvider):
        """fetch_price_data handles empty/invalid response gracefully."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, []))

            with pytest.raises(DataProviderError) as exc_info:
                await provider.fetch_price_data("solana")

            assert "invalid ohlc" in str(exc_info.value).lower()

    # ========================================================================
    # fetch_market_data tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_fetch_market_data_returns_expected_keys(self, provider: CoinGeckoProvider):
        """fetch_market_data returns dict with expected keys."""
        mock_data = {
            "solana": {
                "usd": 150.0,
                "usd_24h_vol": 5000000000.0,
                "usd_24h_change": 2.5,
                "usd_market_cap": 75000000000.0,
            }
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, mock_data))

            result = await provider.fetch_market_data("solana")

        assert "price" in result
        assert "volume_24h" in result
        assert "price_change_24h" in result
        assert "market_cap" in result
        assert result["price"] == 150.0
        assert result["volume_24h"] == 5000000000.0
        assert result["price_change_24h"] == 2.5
        assert result["market_cap"] == 75000000000.0

    @pytest.mark.asyncio
    async def test_fetch_market_data_token_not_found(self, provider: CoinGeckoProvider):
        """fetch_market_data handles token not found in response."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, {}))

            with pytest.raises(DataProviderError) as exc_info:
                await provider.fetch_market_data("nonexistenttoken")

            assert "not found" in str(exc_info.value).lower()

    # ========================================================================
    # health_check tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self, provider: CoinGeckoProvider):
        """health_check returns True when API is accessible."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, {"gecko_sAYS": "(●|●)"}))

            result = await provider.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_returns_false_on_error(self, provider: CoinGeckoProvider):
        """health_check returns False on network error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.side_effect = Exception("Network error")

            result = await provider.health_check()

        assert result is False

    # ========================================================================
    # search_token tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_token_returns_list(self, provider: CoinGeckoProvider):
        """search_token returns list of matching coins."""
        mock_data = {
            "coins": [
                {
                    "id": "solana",
                    "name": "Solana",
                    "symbol": "sol",
                    "thumb": "https://assets.coingecko.com/coins/images/4128/thumb/solana.jpg",
                },
                {
                    "id": "solana-protocol",
                    "name": "Solana Protocol",
                    "symbol": "SOLP",
                    "thumb": "https://assets.coingecko.com/coins/images/4128/thumb/solana.jpg",
                },
            ]
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, mock_data))

            result = await provider.search_token("solana")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "solana"
        assert result[0]["name"] == "Solana"
        assert result[0]["symbol"] == "sol"

    @pytest.mark.asyncio
    async def test_search_token_handles_empty_results(self, provider: CoinGeckoProvider):
        """search_token returns empty list when no matches found."""
        mock_data = {"coins": []}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(return_value=make_mock_response(200, mock_data))

            result = await provider.search_token("nonexistentcoinxyz")

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_search_token_handles_rate_limit(self, provider: CoinGeckoProvider):
        """search_token handles rate limiting gracefully by returning empty list."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__.return_value = None
            mock_client.return_value.get = AsyncMock(
                return_value=make_mock_response(429, {"error": "rate limit exceeded"})
            )

            result = await provider.search_token("solana")

        assert isinstance(result, list)
        assert len(result) == 0
