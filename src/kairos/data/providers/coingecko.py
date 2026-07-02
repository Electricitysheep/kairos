"""CoinGecko API provider — free tier, broad market data."""

from __future__ import annotations

import httpx
import pandas as pd

from kairos.data.providers.base import DataProvider, DataProviderError


class CoinGeckoProvider(DataProvider):
    """CoinGecko API provider — free tier, broad market data.

    CoinGecko provides free access to market data with rate limiting:
    - Free tier: 10-30 calls/minute
    - Pro tier: higher limits with API key

    Token should be a CoinGecko coin ID (e.g., "solana", "bitcoin", "ethereum").
    Use search_token() to find coin IDs by name or symbol.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key: str = ""):
        """Initialize CoinGecko provider.

        Args:
            api_key: CoinGecko Pro API key (optional, defaults to free tier).
        """
        self.api_key = api_key

    def _get_headers(self) -> dict:
        """Get HTTP headers for requests."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key
        return headers

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if response.status_code == 429:
            raise DataProviderError(
                "CoinGecko rate limit exceeded. Free tier allows 10-30 calls/minute. "
                "Consider adding an API key or waiting before making more requests."
            )
        elif response.status_code == 404:
            raise DataProviderError(f"Token not found on CoinGecko: {response.url}")
        elif response.status_code >= 400:
            raise DataProviderError(f"CoinGecko API error ({response.status_code}): {response.text}")

    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        """Fetch OHLCV price data.

        Args:
            token: CoinGecko coin ID (e.g., "solana", "bitcoin").
            days: Days of historical data (1, 7, 14, 30, 90, 180, 365, max).

        Returns:
            DataFrame with columns: open, high, low, close, volume.
            Note: CoinGecko OHLC endpoint does not include volume, so volume
            is set to 0 for all rows.

        Raises:
            DataProviderError: If token not found or rate limited.
        """
        url = f"{self.BASE_URL}/coins/{token}/ohlc"
        params: dict[str, str | int] = {"days": days, "vs_currency": "usd"}

        async with httpx.AsyncClient(headers=self._get_headers()) as client:
            try:
                response = await client.get(url, params=params, timeout=30)
            except httpx.TimeoutException:
                raise DataProviderError("CoinGecko request timed out")
            except httpx.RequestError as e:
                raise DataProviderError(f"CoinGecko request failed: {e}")

            self._handle_error(response)

            data = response.json()
            if not data or not isinstance(data, list):
                raise DataProviderError(f"Invalid OHLC data for token: {token}")

        # CoinGecko returns [[timestamp, open, high, low, close], ...]
        df = pd.DataFrame(
            data,
            columns=["timestamp", "open", "high", "low", "close"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df["volume"] = 0  # CoinGecko OHLC doesn't include volume

        result = df[["open", "high", "low", "close", "volume"]].copy()
        result.index.name = "timestamp"
        return result

    async def fetch_market_data(self, token: str) -> dict:
        """Fetch current market data for a token.

        Args:
            token: CoinGecko coin ID (e.g., "solana", "bitcoin").

        Returns:
            Dict with keys: price, volume_24h, price_change_24h, market_cap.

        Raises:
            DataProviderError: If token not found or rate limited.
        """
        url = f"{self.BASE_URL}/simple/price"
        params = {
            "ids": token,
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_market_cap": "true",
        }

        async with httpx.AsyncClient(headers=self._get_headers()) as client:
            try:
                response = await client.get(url, params=params, timeout=30)
            except httpx.TimeoutException:
                raise DataProviderError("CoinGecko request timed out")
            except httpx.RequestError as e:
                raise DataProviderError(f"CoinGecko request failed: {e}")

            self._handle_error(response)

            data = response.json()
            if token not in data:
                raise DataProviderError(f"Token not found on CoinGecko: {token}")

        token_data = data[token]
        return {
            "price": token_data.get("usd", 0),
            "volume_24h": token_data.get("usd_24h_vol", 0),
            "price_change_24h": token_data.get("usd_24h_change", 0),
            "market_cap": token_data.get("usd_market_cap", 0),
        }

    async def health_check(self) -> bool:
        """Check if CoinGecko API is accessible.

        Returns:
            True if API is healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient(headers=self._get_headers()) as client:
                r = await client.get(f"{self.BASE_URL}/ping", timeout=10)
                return r.status_code == 200
        except Exception:
            return False

    async def search_token(self, query: str) -> list[dict]:
        """Search for a token by name or symbol.

        Helper method to find CoinGecko coin IDs for other methods.

        Args:
            query: Search query (token name or symbol).

        Returns:
            List of matching coins with keys: id, name, symbol, thumb.
            Empty list if no matches found.
        """
        url = f"{self.BASE_URL}/search"
        params = {"query": query}

        async with httpx.AsyncClient(headers=self._get_headers()) as client:
            try:
                response = await client.get(url, params=params, timeout=30)
            except httpx.TimeoutException:
                return []
            except httpx.RequestError:
                return []

        if response.status_code == 429:
            # Don't raise on search, just return empty
            return []
        elif response.status_code >= 400:
            return []

        data = response.json()
        coins = data.get("coins", [])
        return [
            {
                "id": coin["id"],
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "thumb": coin.get("thumb", ""),
            }
            for coin in coins
        ]
