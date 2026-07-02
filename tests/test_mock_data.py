"""Tests for mock data providers."""

from __future__ import annotations

import pandas as pd

from kairos.data import MockDataProvider


class TestMockDataProvider:
    """Tests for MockDataProvider class."""

    def test_generate_price_data_columns(self):
        """DataFrame has correct columns."""
        df = MockDataProvider.generate_price_data(days=1)
        expected_cols = {"open", "high", "low", "close", "volume"}
        assert set(df.columns) == expected_cols

    def test_generate_price_data_row_count(self):
        """DataFrame has correct number of rows (24 per day)."""
        df = MockDataProvider.generate_price_data(days=5)
        assert len(df) == 5 * 24

    def test_generate_price_data_ohlcv_positive(self):
        """All OHLCV values are positive."""
        df = MockDataProvider.generate_price_data(days=3)
        assert (df["open"] > 0).all()
        assert (df["high"] > 0).all()
        assert (df["low"] > 0).all()
        assert (df["close"] > 0).all()
        assert (df["volume"] >= 0).all()

    def test_generate_price_data_high_ge_low(self):
        """High >= Low for all rows."""
        df = MockDataProvider.generate_price_data(days=3)
        assert (df["high"] >= df["low"]).all()

    def test_generate_price_data_reproducible(self):
        """Same seed produces same data."""
        df1 = MockDataProvider.generate_price_data(days=3, seed=123)
        df2 = MockDataProvider.generate_price_data(days=3, seed=123)
        pd.testing.assert_frame_equal(df1, df2)

    def test_generate_price_data_datetime_index(self):
        """DataFrame has hourly DatetimeIndex."""
        df = MockDataProvider.generate_price_data(days=1)
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.freq is not None or len(df.index) == 24

    def test_generate_research_packet_keys(self):
        """Research packet has expected keys."""
        packet = MockDataProvider.generate_research_packet(seed=42)
        expected_keys = {"token", "price_summary", "volume_24h", "technical_summary", "data_quality"}
        assert set(packet.keys()) == expected_keys

    def test_generate_research_packet_price_summary_keys(self):
        """price_summary has expected keys."""
        packet = MockDataProvider.generate_research_packet(seed=42)
        expected_keys = {"current", "high_24h", "low_24h", "change_24h"}
        assert set(packet["price_summary"].keys()) == expected_keys

    def test_generate_research_packet_reproducible(self):
        """Same seed produces same packet."""
        p1 = MockDataProvider.generate_research_packet(seed=99)
        p2 = MockDataProvider.generate_research_packet(seed=99)
        assert p1 == p2

    def test_generate_technical_signals_keys(self):
        """Technical signals has expected structure."""
        signals = MockDataProvider.generate_technical_signals(seed=42)
        assert "rsi" in signals
        assert "macd" in signals
        assert "bollinger_bands" in signals

    def test_generate_technical_signals_rsi_range(self):
        """RSI is within valid range."""
        signals = MockDataProvider.generate_technical_signals(seed=42)
        assert 0 <= signals["rsi"] <= 100

    def test_generate_technical_signals_macd_structure(self):
        """MACD has line, signal, histogram."""
        signals = MockDataProvider.generate_technical_signals(seed=42)
        assert set(signals["macd"].keys()) == {"line", "signal", "histogram"}
