"""Mock data providers for testing and development."""

from __future__ import annotations

import numpy as np
import pandas as pd


class MockDataProvider:
    """Static mock data generator for Kairos."""

    @staticmethod
    def generate_price_data(days: int = 30, seed: int = 42) -> pd.DataFrame:
        """Generate OHLCV price data using random walk.

        Args:
            days: Number of days of hourly data.
            seed: Random seed for reproducibility.

        Returns:
            DataFrame with hourly DatetimeIndex and columns:
            open, high, low, close, volume
        """
        rng = np.random.default_rng(seed)
        n = days * 24

        # Random walk for close prices
        returns = rng.standard_normal(n) * 0.02  # ~2% daily vol
        closes = 100 * np.exp(np.cumsum(returns))

        # Generate OHLC around close
        daily_range = rng.uniform(0.005, 0.03, n)

        opens = closes + rng.normal(0, closes * 0.005, n)
        highs = np.maximum(closes, opens) + rng.uniform(0, closes * daily_range * 0.5, n)
        lows = np.minimum(closes, opens) - rng.uniform(0, closes * daily_range * 0.5, n)
        lows = np.maximum(lows, closes * 0.1)  # Ensure positive

        volumes = rng.lognormal(15, 1, n)

        df = pd.DataFrame(
            {
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
            },
            index=pd.date_range(start="2025-01-01", periods=n, freq="h"),
        )

        # Ensure high >= low for all rows
        df["high"] = df[["high", "low"]].max(axis=1)

        # Ensure non-negative
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].clip(lower=0.01)

        df["volume"] = df["volume"].clip(lower=0)

        return df

    @staticmethod
    def generate_research_packet(token: str = "SOL/USDT", seed: int = 42) -> dict:
        """Generate a simulated research packet for a token.

        Args:
            token: Trading pair symbol.
            seed: Random seed for reproducibility.

        Returns:
            Dict with keys: token, price_summary, volume_24h,
            technical_summary, data_quality
        """
        rng = np.random.default_rng(seed)

        current = rng.uniform(80, 150)
        change_24h = rng.uniform(-10, 10)

        price_summary = {
            "current": round(current, 2),
            "high_24h": round(current * (1 + rng.uniform(0, 0.05)), 2),
            "low_24h": round(current * (1 - rng.uniform(0, 0.05)), 2),
            "change_24h": round(change_24h, 2),
        }

        volume_24h = float(rng.lognormal(20, 2))

        technical_summary = (
            f"Bullish momentum on {token} with RSI at {rng.integers(45, 70)}. "
            f"MACD histogram showing increasing bullish divergence. "
            f"Price holding above key support levels with strong volume confirmation."
        )

        data_quality = rng.choice(["excellent", "good", "fair"])

        return {
            "token": token,
            "price_summary": price_summary,
            "volume_24h": volume_24h,
            "technical_summary": technical_summary,
            "data_quality": data_quality,
        }

    @staticmethod
    def generate_technical_signals(seed: int = 42) -> dict:
        """Generate simulated technical indicator signals.

        Args:
            seed: Random seed for reproducibility.

        Returns:
            Dict with RSI, MACD, and Bollinger Bands info.
        """
        rng = np.random.default_rng(seed)

        rsi = rng.uniform(40, 70)
        macd_line = rng.uniform(-5, 5)
        macd_signal = rng.uniform(-4, 4)
        macd_histogram = macd_line - macd_signal

        bb_position = rng.uniform(0.2, 0.8)

        return {
            "rsi": round(rsi, 2),
            "macd": {
                "line": round(macd_line, 4),
                "signal": round(macd_signal, 4),
                "histogram": round(macd_histogram, 4),
            },
            "bollinger_bands": {
                "position": round(bb_position, 4),
                "upper": round(100 * rng.uniform(1.01, 1.05), 2),
                "middle": round(100, 2),
                "lower": round(100 * rng.uniform(0.95, 0.99), 2),
            },
        }