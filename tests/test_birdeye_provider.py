"""Tests for BirdeyeProvider data provider."""

from __future__ import annotations

import httpx
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kairos.data.providers.base import DataProviderError
from kairos.data.providers.birdeye import BirdeyeProvider


class TestBirdeyeProvider:
    """Tests for BirdeyeProvider class."""

    @pytest.mark.asyncio
    async def test_requires_api_key(self):
        """Provider requires API key for real data."""
        provider = BirdeyeProvider(api_key="")
        with pytest.raises(DataProviderError, match="API key required"):
            await provider.fetch_price_data("So11111111111111111111111111111111111111112")

    @pytest.mark.asyncio
    async def test_fetch_market_data_requires_api_key(self):
        """fetch_market_data also requires API key."""
        provider = BirdeyeProvider(api_key="")
        with pytest.raises(DataProviderError, match="API key required"):
            await provider.fetch_market_data("So11111111111111111111111111111111111111112")

    @pytest.mark.asyncio
    async def test_fetch_price_data_success(self):
        """With API key, returns expected DataFrame structure on success."""
        provider = BirdeyeProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "items": [
                    {
                        "t": 1700000000,
                        "o": "100.0",
                        "h": "105.0",
                        "l": "99.0",
                        "c": "102.0",
                        "v": "1000.0",
                    },
                    {
                        "t": 1700003600,
                        "o": "102.0",
                        "h": "107.0",
                        "l": "101.0",
                        "c": "104.0",
                        "v": "1200.0",
                    },
                ]
            }
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            df = await provider.fetch_price_data(
                "So11111111111111111111111111111111111111112", days=1
            )

        assert set(df.columns) == {"open", "high", "low", "close", "volume"}
        assert len(df) == 2
        assert df["open"].iloc[0] == 100.0
        assert df["high"].iloc[0] == 105.0
        assert df["low"].iloc[0] == 99.0
        assert df["close"].iloc[0] == 102.0
        assert df["volume"].iloc[0] == 1000.0

    @pytest.mark.asyncio
    async def test_fetch_market_data_success(self):
        """With API key, fetch_market_data returns expected structure."""
        provider = BirdeyeProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "value": "150.25",
                "volume24h": "1000000.50",
                "priceChange24h": "2.5",
            }
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            result = await provider.fetch_market_data(
                "So11111111111111111111111111111111111111112"
            )

        assert "price" in result
        assert result["price"] == 150.25
        assert result["volume_24h"] == "1000000.50"
        assert result["price_change_24h"] == "2.5"
        assert result["market_cap"] is None

    @pytest.mark.asyncio
    async def test_handles_http_error(self):
        """Handles HTTP errors gracefully."""
        provider = BirdeyeProvider(api_key="test-key")

        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock()
            mock_get.side_effect = httpx.HTTPStatusError(
                "Not Found",
                request=MagicMock(),
                response=MagicMock(status_code=404),
            )
            mock_client.return_value.__aenter__.return_value.get = mock_get

            with pytest.raises(DataProviderError, match="HTTP error"):
                await provider.fetch_price_data(
                    "So11111111111111111111111111111111111111112"
                )

    @pytest.mark.asyncio
    async def test_handles_network_error(self):
        """Handles network errors gracefully."""
        provider = BirdeyeProvider(api_key="test-key")

        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock()
            mock_get.side_effect = httpx.RequestError("Connection failed")
            mock_client.return_value.__aenter__.return_value.get = mock_get

            with pytest.raises(DataProviderError, match="request failed"):
                await provider.fetch_price_data(
                    "So11111111111111111111111111111111111111112"
                )

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_unreachable(self):
        """health_check returns False when API is unreachable."""
        provider = BirdeyeProvider(api_key="test-key")

        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock()
            mock_get.side_effect = httpx.RequestError("Connection failed")
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await provider.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_returns_true_on_success(self):
        """health_check returns True when API is accessible."""
        provider = BirdeyeProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"value": "150.0"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_fetch_price_data_handles_empty_items(self):
        """Handles empty items list."""
        provider = BirdeyeProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"items": []}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(DataProviderError, match="No price data"):
                await provider.fetch_price_data(
                    "So11111111111111111111111111111111111111112"
                )