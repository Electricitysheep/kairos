"""Birdeye API provider for Solana token data."""

from __future__ import annotations

import httpx
import pandas as pd

from kairos.data.providers.base import DataProvider, DataProviderError


class BirdeyeProvider(DataProvider):
    """Birdeye API provider for Solana token data."""

    BASE_URL = "https://public-api.birdeye.so/public"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        """Fetch OHLCV price data.

        Uses Birdeye price/multiple endpoint.
        Handles API errors gracefully.
        Returns DataFrame with columns: open, high, low, close, volume
        """
        if not self.api_key:
            raise DataProviderError("Birdeye API key required. Set BIRDEYE_API_KEY environment variable.")

        from_time = pd.Timestamp.now() - pd.Timedelta(days=days)
        to_time = pd.Timestamp.now()

        if pd.isna(from_time) or pd.isna(to_time):
            raise DataProviderError("Invalid timestamp calculation")

        url = f"{self.BASE_URL}/price/multiple"
        params: dict[str, str | int] = {
            "address": token,
            "from": int(from_time.value / 1e9),
            "to": int(to_time.value / 1e9),
        }
        headers = {"X-API-KEY": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            raise DataProviderError(f"Birdeye API HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise DataProviderError(f"Birdeye API request failed: {e}")
        except ValueError as e:
            raise DataProviderError(f"Birdeye API JSON parse error: {e}")

        items = data.get("data", {}).get("items", [])
        if not items:
            raise DataProviderError(f"No price data returned for {token}")

        records = []
        for item in items:
            try:
                records.append(
                    {
                        "open": float(item["o"]),
                        "high": float(item["h"]),
                        "low": float(item["l"]),
                        "close": float(item["c"]),
                        "volume": float(item["v"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue

        if not records:
            raise DataProviderError(f"Failed to parse price data for {token}")

        df = pd.DataFrame(records)
        df.index = pd.to_datetime(df.index, unit="s")
        return df

    async def fetch_market_data(self, token: str) -> dict:
        """Fetch current market data for a token.

        Uses Birdeye price endpoint for current price + 24h change.
        """
        if not self.api_key:
            raise DataProviderError("Birdeye API key required. Set BIRDEYE_API_KEY environment variable.")

        url = f"{self.BASE_URL}/price"
        params = {"address": token}
        headers = {"X-API-KEY": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            raise DataProviderError(f"Birdeye API HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise DataProviderError(f"Birdeye API request failed: {e}")
        except ValueError as e:
            raise DataProviderError(f"Birdeye API JSON parse error: {e}")

        result = data.get("data", {})
        if not result:
            raise DataProviderError(f"No market data returned for {token}")

        return {
            "price": float(result.get("value", 0)),
            "volume_24h": result.get("volume24h"),
            "price_change_24h": result.get("priceChange24h"),
            "market_cap": None,
        }

    async def health_check(self) -> bool:
        """Check if Birdeye API is accessible."""
        try:
            await self.fetch_market_data("So11111111111111111111111111111111111111112")
            return True
        except Exception:
            return False
