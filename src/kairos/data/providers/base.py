"""Abstract base class for data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class DataProviderError(Exception):
    """Raised when a data provider fails to fetch data."""


class DataProvider(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    async def fetch_price_data(self, token: str, days: int = 30) -> pd.DataFrame:
        """Fetch OHLCV price data for a token.

        Args:
            token: Token address or symbol.
            days: Days of historical data.

        Returns:
            DataFrame with columns: open, high, low, close, volume
        """

    @abstractmethod
    async def fetch_market_data(self, token: str) -> dict:
        """Fetch current market summary for a token.

        Args:
            token: Token address or symbol.

        Returns:
            Dict with keys: price, volume_24h, price_change_24h, market_cap (if available)
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider API is accessible.

        Returns:
            True if healthy, False otherwise.
        """
