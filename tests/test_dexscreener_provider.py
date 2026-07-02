"""Tests for DexScreenerProvider data provider."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from kairos.data.providers.base import DataProviderError
from kairos.data.providers.dexscreener import DexScreenerProvider


class TestDexScreenerProvider:
    """Tests for DexScreenerProvider class."""

    def test_works_without_api_key(self):
        """Provider works without API key (DexScreener is free)."""
        provider = DexScreenerProvider(api_key="")
        assert provider._api_key == ""
        # No exception raised

    def test_works_with_empty_api_key(self):
        """Provider works with empty string API key."""
        provider = DexScreenerProvider()
        assert provider._api_key == ""

    @pytest.mark.asyncio
    async def test_fetch_market_data_returns_expected_structure(self):
        """fetch_market_data returns dict with expected keys."""
        provider = DexScreenerProvider()

        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "pairs": [
                {
                    "pairAddress": "ExamplePair123",
                    "priceUsd": "150.25",
                    "volume": {"h24": 1000000.50},
                    "priceChange": {"h24": 2.5},
                    "liquidity": {"usd": 500000.0},
                    "fdv": 15000000.0,
                    "dexId": "raydium",
                }
            ]
        }

        with patch.object(provider, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_search_response)

            result = await provider.fetch_market_data("SOL")

        assert "price" in result
        assert result["price"] == 150.25
        assert result["volume_24h"] == 1000000.50
        assert result["price_change_24h"] == 2.5
        assert result["liquidity"] == 500000.0
        assert result["fdv"] == 15000000.0
        assert result["pair_address"] == "ExamplePair123"
        assert result["dex"] == "raydium"

    @pytest.mark.asyncio
    async def test_fetch_price_data_returns_dataframe_structure(self):
        """fetch_price_data returns DataFrame with correct columns."""
        provider = DexScreenerProvider()

        mock_candle = MagicMock()
        mock_candle.json.return_value = {
            "candles": [
                {
                    "t": 1700000000000,
                    "o": "100.0",
                    "h": "105.0",
                    "l": "99.0",
                    "c": "102.0",
                    "v": "1000.0",
                },
                {
                    "t": 1700003600000,
                    "o": "102.0",
                    "h": "107.0",
                    "l": "101.0",
                    "c": "104.0",
                    "v": "1200.0",
                },
            ]
        }

        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "pairs": [
                {
                    "pairAddress": "ExamplePair123",
                    "priceUsd": "150.0",
                    "liquidity": {"usd": 500000.0},
                }
            ]
        }

        with patch.object(provider, "_client") as mock_client:
            mock_get = AsyncMock(
                side_effect=[mock_search_response, mock_candle]
            )
            mock_client.get = mock_get

            df = await provider.fetch_price_data("SOL", days=1)

        assert set(df.columns) == {"open", "high", "low", "close", "volume"}
        assert len(df) == 2
        assert df["open"].iloc[0] == 100.0
        assert df["high"].iloc[0] == 105.0
        assert df["low"].iloc[0] == 99.0
        assert df["close"].iloc[0] == 102.0
        assert df["volume"].iloc[0] == 1000.0

    @pytest.mark.asyncio
    async def test_handles_404_token_not_found(self):
        """Handles 404 when token is not found."""
        provider = DexScreenerProvider()

        with patch.object(provider, "_client") as mock_client:
            mock_get = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Not Found",
                    request=MagicMock(),
                    response=MagicMock(status_code=404),
                )
            )
            mock_client.get = mock_get

            with pytest.raises(DataProviderError, match="Token not found"):
                await provider.fetch_market_data("NONEXISTENTTOKENXYZ")

    @pytest.mark.asyncio
    async def test_handles_empty_pairs_list(self):
        """Handles empty pairs list gracefully."""
        provider = DexScreenerProvider()

        mock_response = MagicMock()
        mock_response.json.return_value = {"pairs": []}

        with patch.object(provider, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            with pytest.raises(DataProviderError, match="No pairs found"):
                await provider.fetch_market_data("NONEXISTENTTOKENXYZ")

    @pytest.mark.asyncio
    async def test_health_check_returns_true_on_success(self):
        """health_check returns True when API is accessible."""
        provider = DexScreenerProvider()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "pairs": [
                {
                    "pairAddress": "SolPair123",
                    "priceUsd": "150.0",
                    "volume": {"h24": 1000000.0},
                    "priceChange": {"h24": 2.5},
                    "liquidity": {"usd": 500000.0},
                    "fdv": 15000000.0,
                    "dexId": "raydium",
                }
            ]
        }

        with patch.object(provider, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_unreachable(self):
        """health_check returns False when API is unreachable."""
        provider = DexScreenerProvider()

        with patch.object(provider, "_client") as mock_client:
            mock_get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
            mock_client.get = mock_get

            result = await provider.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_returns_false_on_404(self):
        """health_check returns False when token not found."""
        provider = DexScreenerProvider()

        with patch.object(provider, "_client") as mock_client:
            mock_get = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Not Found",
                    request=MagicMock(),
                    response=MagicMock(status_code=404),
                )
            )
            mock_client.get = mock_get

            result = await provider.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_fetch_price_data_handles_no_candles(self):
        """Handles empty candles list."""
        provider = DexScreenerProvider()

        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "pairs": [
                {
                    "pairAddress": "ExamplePair123",
                    "liquidity": {"usd": 500000.0},
                }
            ]
        }

        mock_candle_response = MagicMock()
        mock_candle_response.json.return_value = {"candles": []}

        with patch.object(provider, "_client") as mock_client:
            mock_get = AsyncMock(
                side_effect=[mock_search_response, mock_candle_response]
            )
            mock_client.get = mock_get

            with pytest.raises(DataProviderError, match="No candle data"):
                await provider.fetch_price_data("SOL", days=1)

    @pytest.mark.asyncio
    async def test_uses_highest_liquidity_pair(self):
        """fetch_market_data selects pair with highest liquidity."""
        provider = DexScreenerProvider()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "pairs": [
                {
                    "pairAddress": "LowLiquidityPair",
                    "priceUsd": "100.0",
                    "volume": {"h24": 10000.0},
                    "priceChange": {"h24": 1.0},
                    "liquidity": {"usd": 10000.0},
                    "fdv": 1000000.0,
                    "dexId": "orca",
                },
                {
                    "pairAddress": "HighLiquidityPair",
                    "priceUsd": "150.0",
                    "volume": {"h24": 5000000.0},
                    "priceChange": {"h24": 2.5},
                    "liquidity": {"usd": 5000000.0},
                    "fdv": 15000000.0,
                    "dexId": "raydium",
                },
            ]
        }

        with patch.object(provider, "_client") as mock_client:
            mock_client.get = AsyncMock(return_value=mock_response)

            result = await provider.fetch_market_data("SOL")

        # Should return the high liquidity pair
        assert result["pair_address"] == "HighLiquidityPair"
        assert result["liquidity"] == 5000000.0
        assert result["price"] == 150.0

    @pytest.mark.asyncio
    async def test_close_closes_client(self):
        """close() properly closes the HTTP client."""
        provider = DexScreenerProvider()
        await provider.close()
        # No exception means success
