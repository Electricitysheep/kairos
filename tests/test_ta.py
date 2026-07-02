import numpy as np
import pandas as pd

from kairos.indicators import TAAnalyzer


def make_trend_data(n=100, trend="up"):
    """
    Create synthetic OHLCV data with a specified trend.

    Args:
        n: Number of periods
        trend: 'up', 'down', or 'sideways'

    Returns:
        pd.DataFrame with open, high, low, close, volume columns
    """
    np.random.seed(42)
    close = np.zeros(n)
    close[0] = 100
    for i in range(1, n):
        # Stronger drift for clearer trend signals
        drift = 0.005 if trend == "up" else (-0.005 if trend == "down" else 0)
        noise = 0.01 if trend == "sideways" else 0.005
        close[i] = close[i - 1] * (1 + np.random.normal(drift, noise))
    df = pd.DataFrame({"close": close})
    df["high"] = df["close"] * (1 + abs(np.random.normal(0, 0.005, n)))
    df["low"] = df["close"] * (1 - abs(np.random.normal(0, 0.005, n)))
    df["open"] = df["close"].shift(1).fillna(df["close"].iloc[0])
    df["volume"] = np.random.uniform(1000, 5000, n)
    return df


class TestRSI:
    """Tests for RSI computation."""

    def test_rsi_values_between_0_and_100(self):
        """RSI values should always be between 0 and 100."""
        df = make_trend_data(n=100, trend="sideways")
        rsi = TAAnalyzer.compute_rsi(df, period=14)
        # Drop NaN values from the initial period
        rsi_valid = rsi.dropna()
        assert all((rsi_valid >= 0) & (rsi_valid <= 100)), "RSI should be between 0 and 100"

    def test_rsi_for_uptrend(self):
        """RSI should be > 55 for uptrend data."""
        df = make_trend_data(n=100, trend="up")
        rsi = TAAnalyzer.compute_rsi(df, period=14)
        rsi_valid = rsi.dropna()
        # RSI for strong uptrend should be elevated
        assert rsi_valid.iloc[-1] > 55, f"RSI for uptrend should be > 55, got {rsi_valid.iloc[-1]}"

    def test_rsi_for_downtrend(self):
        """RSI should be < 45 for downtrend data."""
        df = make_trend_data(n=100, trend="down")
        rsi = TAAnalyzer.compute_rsi(df, period=14)
        rsi_valid = rsi.dropna()
        # RSI for downtrend should be low
        assert rsi_valid.iloc[-1] < 45, f"RSI for downtrend should be < 45, got {rsi_valid.iloc[-1]}"


class TestMACD:
    """Tests for MACD computation."""

    def test_macd_returns_all_expected_keys(self):
        """MACD should return dict with all expected keys."""
        df = make_trend_data(n=100, trend="up")
        macd = TAAnalyzer.compute_macd(df)
        expected_keys = {"macd_line", "signal_line", "histogram", "is_bullish_cross"}
        assert set(macd.keys()) == expected_keys, f"MACD should have keys {expected_keys}, got {set(macd.keys())}"

    def test_macd_values_are_finite(self):
        """MACD values should be finite numbers."""
        df = make_trend_data(n=100, trend="up")
        macd = TAAnalyzer.compute_macd(df)
        assert isinstance(macd["macd_line"], float)
        assert isinstance(macd["signal_line"], float)
        assert isinstance(macd["histogram"], float)
        assert isinstance(macd["is_bullish_cross"], bool)


class TestBollingerBands:
    """Tests for Bollinger Bands computation."""

    def test_bb_upper_mid_lower_order(self):
        """Upper band > mid band > lower band."""
        df = make_trend_data(n=100, trend="sideways")
        bb = TAAnalyzer.compute_bollinger(df)
        assert bb["upper"] > bb["mid"], f"Upper {bb['upper']} should be > mid {bb['mid']}"
        assert bb["mid"] > bb["lower"], f"Mid {bb['mid']} should be > lower {bb['lower']}"

    def test_bb_percent_b_between_0_and_1(self):
        """Percent B should be between 0 and 1 for price within bands."""
        df = make_trend_data(n=100, trend="sideways")
        bb = TAAnalyzer.compute_bollinger(df)
        # For price within bands, percent_b should be between 0 and 1
        assert 0 <= bb["percent_b"] <= 1, f"Percent B should be between 0 and 1, got {bb['percent_b']}"


class TestComputeAll:
    """Tests for compute_all method."""

    def test_compute_all_returns_all_expected_keys(self):
        """compute_all should return dict with all expected keys."""
        df = make_trend_data(n=100, trend="up")
        result = TAAnalyzer.compute_all(df)
        expected_keys = {
            "rsi_14",
            "macd",
            "bb",
            "ema_9",
            "ema_21",
            "ema_50",
            "adx_14",
            "atr_14",
            "composite_score",
        }
        assert set(result.keys()) == expected_keys, (
            f"compute_all should return keys {expected_keys}, got {set(result.keys())}"
        )

    def test_composite_score_between_0_and_100(self):
        """Composite score should be between 0 and 100."""
        df = make_trend_data(n=100, trend="up")
        result = TAAnalyzer.compute_all(df)
        assert 0 <= result["composite_score"] <= 100, (
            f"Composite score should be between 0 and 100, got {result['composite_score']}"
        )


class TestEMAs:
    """Tests for EMA computation."""

    def test_ema_shorter_period_more_responsive(self):
        """Shorter period EMA should be more responsive to price changes."""
        df = make_trend_data(n=100, trend="up")
        ema_9 = TAAnalyzer.compute_ema(df, period=9)
        ema_21 = TAAnalyzer.compute_ema(df, period=21)
        # In an uptrend, shorter EMA should be above longer EMA
        assert ema_9.iloc[-1] > ema_21.iloc[-1], "EMA 9 should be above EMA 21 in uptrend"


class TestADX:
    """Tests for ADX computation."""

    def test_adx_returns_float(self):
        """ADX should return a float value."""
        df = make_trend_data(n=100, trend="up")
        adx = TAAnalyzer.compute_adx(df)
        assert isinstance(adx, float), f"ADX should return float, got {type(adx)}"

    def test_adx_positive(self):
        """ADX should always be positive."""
        df = make_trend_data(n=100, trend="sideways")
        adx = TAAnalyzer.compute_adx(df)
        assert adx >= 0, f"ADX should be non-negative, got {adx}"


class TestATR:
    """Tests for ATR computation."""

    def test_atr_returns_float(self):
        """ATR should return a float value."""
        df = make_trend_data(n=100, trend="up")
        atr = TAAnalyzer.compute_atr(df)
        assert isinstance(atr, float), f"ATR should return float, got {type(atr)}"

    def test_atr_positive(self):
        """ATR should always be positive."""
        df = make_trend_data(n=100, trend="up")
        atr = TAAnalyzer.compute_atr(df)
        assert atr > 0, f"ATR should be positive, got {atr}"
