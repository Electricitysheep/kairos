"""Tests for the Yahoo Finance data provider."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from kairos.data.providers.base import DataProviderError
from kairos.data.providers.yahoofinance import YahooFinanceProvider


def _history_df(rows: int = 3) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            "Open": [10.0] * rows,
            "High": [11.0] * rows,
            "Low": [9.0] * rows,
            "Close": [10.0 + i for i in range(rows)],
            "Volume": [1000] * rows,
        },
        index=idx,
    )


def _patch_ticker(ticker):
    return patch("kairos.data.providers.yahoofinance.yf.Ticker", return_value=ticker)


class TestYahooFinanceProvider:
    def test_fetch_price_data_normalizes_columns(self):
        ticker = MagicMock()
        ticker.history.return_value = _history_df()
        with _patch_ticker(ticker):
            df = asyncio.run(YahooFinanceProvider().fetch_price_data("AAPL", days=5))
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]

    def test_empty_history_raises(self):
        ticker = MagicMock()
        ticker.history.return_value = pd.DataFrame()
        with _patch_ticker(ticker):
            with pytest.raises(DataProviderError, match="No data"):
                asyncio.run(YahooFinanceProvider().fetch_price_data("NOPE"))

    def test_underlying_error_is_wrapped(self):
        ticker = MagicMock()
        ticker.history.side_effect = RuntimeError("network down")
        with _patch_ticker(ticker):
            with pytest.raises(DataProviderError, match="Failed to fetch"):
                asyncio.run(YahooFinanceProvider().fetch_price_data("AAPL"))

    def test_fetch_market_data_computes_change(self):
        ticker = MagicMock()
        ticker.history.return_value = _history_df(rows=2)  # close 10.0 -> 11.0
        ticker.info = {"marketCap": 1_000_000}
        with _patch_ticker(ticker):
            data = asyncio.run(YahooFinanceProvider().fetch_market_data("AAPL"))
        assert data["price"] == 11.0
        assert data["price_change_24h"] == 10.0  # +10%
        assert data["market_cap"] == 1_000_000

    def test_fetch_market_data_swallows_errors(self):
        ticker = MagicMock()
        ticker.history.side_effect = RuntimeError("boom")
        with _patch_ticker(ticker):
            data = asyncio.run(YahooFinanceProvider().fetch_market_data("AAPL"))
        assert data == {"price": 0, "volume_24h": 0, "price_change_24h": 0, "market_cap": None}

    def test_health_check_true_when_data(self):
        ticker = MagicMock()
        ticker.history.return_value = _history_df()
        with _patch_ticker(ticker):
            assert asyncio.run(YahooFinanceProvider().health_check()) is True

    def test_health_check_false_on_error(self):
        ticker = MagicMock()
        ticker.history.side_effect = RuntimeError("boom")
        with _patch_ticker(ticker):
            assert asyncio.run(YahooFinanceProvider().health_check()) is False
