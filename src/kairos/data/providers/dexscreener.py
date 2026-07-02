"""DexScreener API provider — free, no-auth DEX pair data."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
import pandas as pd

from kairos.data.providers.base import DataProvider, DataProviderError


class DexScreenerProvider(DataProvider):
    """DexScreener API provider — free, no-auth DEX pair data.

    DexScreener provides real-time DEX pair data including price, volume,
    liquidity, and price history (via candles endpoint).

    API Docs: https://docs.dexscreener.com/
    """

    BASE_URL = "https://api.dexscreener.com/latest/dex"

    def __init__(self, api_key: str = "") -> None:
        """Initialize DexScreener provider.

        DexScreener is free and does NOT require an API key.
        The api_key parameter is accepted for interface compatibility but ignored.

        Args:
            api_key: Ignored (present for compatibility).
        """
        self._client = httpx.AsyncClient(timeout=30.0)
        self._api_key = api_key

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        """Fetch OHLCV price data for a token.

        DexScreener provides historical candles via the pairs endpoint.
        We try to get candles for the most liquid pair matching the token.

        Args:
            token: Token address (base58) or symbol.
            days: Days of historical data (approximate, capped by API limits).

        Returns:
            DataFrame with columns: open, high, low, close, volume and
            a DatetimeIndex.

        Raises:
            DataProviderError: If no pair data is available or the token is not found.
        """
        # Search for pairs matching the token
        search_url = f"{self.BASE_URL}/search?q={token}"
        try:
            response = await self._client.get(search_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise DataProviderError(f"Token not found: {token}")
            raise DataProviderError(f"DexScreener HTTP error: {e}")
        except httpx.RequestError as e:
            raise DataProviderError(f"DexScreener request failed: {e}")

        data = response.json()
        pairs = data.get("pairs", [])

        if not pairs:
            raise DataProviderError(f"No pairs found for token: {token}")

        # Sort by liquidity (reserveUSD) descending — take the best pair
        best_pair = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

        pair_address = best_pair.get("pairAddress")
        if not pair_address:
            raise DataProviderError(f"No pair address found for: {token}")

        # Fetch candles for this pair
        candles_url = f"{self.BASE_URL}/pairs/{pair_address}/candles?interval=h1&limit={days * 24}"
        try:
            candles_response = await self._client.get(candles_url)
            candles_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise DataProviderError(f"Candles not found for pair: {pair_address}")
            raise DataProviderError(f"DexScreener candles HTTP error: {e}")
        except httpx.RequestError as e:
            raise DataProviderError(f"DexScreener candles request failed: {e}")

        candles_data = candles_response.json()
        candles = candles_data.get("candles", [])

        if not candles:
            raise DataProviderError(f"No candle data available for: {token}")

        records: list[dict[str, Any]] = []
        for candle in candles:
            records.append(
                {
                    "open": float(candle.get("o", 0)),
                    "high": float(candle.get("h", 0)),
                    "low": float(candle.get("l", 0)),
                    "close": float(candle.get("c", 0)),
                    "volume": float(candle.get("v", 0)),
                    "timestamp": datetime.fromtimestamp(candle.get("t", 0) / 1000),
                }
            )

        df = pd.DataFrame(records)
        if df.empty:
            raise DataProviderError(f"Empty candle DataFrame for: {token}")

        df = df.sort_values("timestamp")
        df.set_index("timestamp", inplace=True)

        return df[["open", "high", "low", "close", "volume"]]  # type: ignore[return-value]

    async def fetch_market_data(self, token: str) -> dict[str, Any]:
        """Fetch current market summary for a token.

        Searches for the token and returns data from the highest-liquidity pair.

        Args:
            token: Token address or symbol.

        Returns:
            Dict with keys:
                - price: current price in USD
                - volume_24h: 24h trading volume in USD
                - price_change_24h: 24h price change in percent
                - liquidity: liquidity in USD
                - fdv: fully diluted valuation in USD
                - pair_address: the DEX pair address
                - dex: DEX name (e.g. "raydium", "orca")

        Raises:
            DataProviderError: If no pairs are found for the token.
        """
        search_url = f"{self.BASE_URL}/search?q={token}"
        try:
            response = await self._client.get(search_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise DataProviderError(f"Token not found: {token}")
            raise DataProviderError(f"DexScreener HTTP error: {e}")
        except httpx.RequestError as e:
            raise DataProviderError(f"DexScreener request failed: {e}")

        data = response.json()
        pairs = data.get("pairs", [])

        if not pairs:
            raise DataProviderError(f"No pairs found for token: {token}")

        # Take the pair with highest liquidity
        best_pair = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

        return {
            "price": float(best_pair.get("priceUsd", 0) or 0),
            "volume_24h": float(best_pair.get("volume", {}).get("h24", 0) or 0),
            "price_change_24h": float(best_pair.get("priceChange", {}).get("h24", 0) or 0),
            "liquidity": float(best_pair.get("liquidity", {}).get("usd", 0) or 0),
            "fdv": float(best_pair.get("fdv", 0) or 0),
            "pair_address": best_pair.get("pairAddress", ""),
            "dex": best_pair.get("dexId", best_pair.get("dex", "")),
        }

    async def health_check(self) -> bool:
        """Check if DexScreener API is accessible.

        Returns:
            True if the API is reachable and returns valid data for SOL,
            False otherwise.
        """
        try:
            await self.fetch_market_data("SOL")
            return True
        except Exception:
            return False
