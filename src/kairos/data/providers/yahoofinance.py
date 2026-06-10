"""Yahoo Finance data provider — free, stocks/ETFs/crypto, no API key needed."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from kairos.data.providers.base import DataProvider, DataProviderError


class YahooFinanceProvider(DataProvider):
    """Free market data provider for stocks, ETFs, crypto, and forex.

    No API key required. Covers US stocks, global ETFs, crypto, and major forex.
    Token format examples:
    - Stocks: "AAPL", "MSFT", "GOOGL"
    - ETFs: "SPY", "QQQ", "GLD"
    - Crypto: "BTC-USD", "ETH-USD", "SOL-USD"
    - Forex: "EURUSD=X", "JPY=X"
    - Index: "^GSPC" (S&P 500), "^IXIC" (NASDAQ)
    """

    def __init__(self, api_key: str = ""):
        pass

    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        try:
            ticker = yf.Ticker(token)
            hist = ticker.history(period=f"{days}d")
            if hist.empty:
                raise DataProviderError(f"No data found for {token}")
            df = hist.rename(columns={
                "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume",
            })
            df = df[["open", "high", "low", "close", "volume"]]
            df.index = pd.to_datetime(df.index)
            return df
        except DataProviderError:
            raise
        except Exception as e:
            raise DataProviderError(f"Failed to fetch {token}: {e}")

    async def fetch_market_data(self, token: str) -> dict:
        try:
            ticker = yf.Ticker(token)
            info = ticker.info or {}
            hist = ticker.history(period="2d")
            price = float(hist["Close"].iloc[-1]) if not hist.empty else 0.0
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
            change = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
            return {
                "price": price,
                "volume_24h": float(hist["Volume"].sum()) if not hist.empty else 0,
                "price_change_24h": round(change, 2),
                "market_cap": info.get("marketCap"),
            }
        except Exception as e:
            return {"price": 0, "volume_24h": 0, "price_change_24h": 0, "market_cap": None}

    async def health_check(self) -> bool:
        try:
            ticker = yf.Ticker("SPY")
            hist = ticker.history(period="5d")
            return not hist.empty
        except Exception:
            return False
