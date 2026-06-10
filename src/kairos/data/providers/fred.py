"""FRED (Federal Reserve Economic Data) provider — free, no API key required for some data."""

from __future__ import annotations

import pandas as pd
import httpx

from kairos.data.providers.base import DataProvider, DataProviderError


class FREDProvider(DataProvider):
    """FRED economic data provider.
    
    Free tier: 120 requests/minute, requires API key (FRED_API_KEY env var).
    Data: GDP, CPI, unemployment, interest rates, and 800,000+ series.
    
    Token format: "GDP", "CPIAUCSL" (CPI), "UNRATE", "FEDFUNDS", "DGS10" (10Y yield)
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: str = ""):
        import os
        self.api_key = api_key or os.environ.get("FRED_API_KEY", "")
    
    async def fetch_price_data(self, token: str, days: int = 365) -> pd.DataFrame:
        if not self.api_key:
            raise DataProviderError("FRED API key required. Set FRED_API_KEY environment variable.")
        
        import json
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/series/observations",
                params={
                    "series_id": token,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": days,
                },
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
        
        observations = data.get("observations", [])
        if not observations:
            raise DataProviderError(f"No data for series: {token}")
        
        records = []
        for obs in observations:
            val = obs.get("value", ".")
            if val == ".":
                continue
            records.append({
                "date": obs["date"],
                "close": float(val),
                "open": float(val),
                "high": float(val),
                "low": float(val),
                "volume": 0,
            })
        
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        return df[["open", "high", "low", "close", "volume"]]
    
    async def fetch_market_data(self, token: str) -> dict:
        df = await self.fetch_price_data(token, days=2)
        if df.empty:
            return {"price": 0, "volume_24h": 0, "price_change_24h": 0, "market_cap": None}
        price = float(df["close"].iloc[-1])
        return {"price": price, "volume_24h": 0, "price_change_24h": 0, "market_cap": None}
    
    async def health_check(self) -> bool:
        return bool(self.api_key)
