"""Technical analysis indicators computed with pandas and numpy."""

from __future__ import annotations

import numpy as np
import pandas as pd


class TAAnalyzer:
    """Technical analysis analyzer for financial time series data."""

    @staticmethod
    def _validate_columns(df: pd.DataFrame, required: list[str]) -> None:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"DataFrame missing required columns: {missing}")

    @staticmethod
    def _compute_tr(df: pd.DataFrame) -> pd.Series:
        """Compute True Range (shared by ADX and ATR)."""
        high, low, close = df["high"], df["low"], df["close"]
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    @staticmethod
    def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Compute RSI using Wilder's smoothing method.

        RSI = 100 - (100 / (1 + RS))
        RS = average_gain / average_loss

        Args:
            df: DataFrame with 'close' column
            period: RSI period (default 14)

        Returns:
            pd.Series with RSI values, same index as input
        """
        close = df["close"]

        # Calculate price changes
        delta = close.diff()

        # Separate gains and losses
        gains = delta.clip(lower=0)
        losses = (-delta).clip(lower=0)

        # Use EMA for smoothing (Wilder's smoothing uses EMA with alpha = 1/period)
        alpha = 1.0 / period

        # Calculate average gains and losses using EMA smoothing
        avg_gain = gains.ewm(alpha=alpha, adjust=False).mean()
        avg_loss = losses.ewm(alpha=alpha, adjust=False).mean()

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def compute_macd(
        df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> dict:
        """
        Compute MACD (Moving Average Convergence Divergence).

        Args:
            df: DataFrame with 'close' column
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)

        Returns:
            dict with keys: macd_line, signal_line, histogram, is_bullish_cross
        """
        close = df["close"]

        # Calculate EMAs
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        # Get latest values
        macd_val = macd_line.iloc[-1]
        signal_val = signal_line.iloc[-1]
        hist_val = histogram.iloc[-1]

        # Check for bullish cross (MACD crossed above signal in latest period)
        if len(macd_line) >= 2:
            is_bullish_cross = bool(
                macd_line.iloc[-1] > signal_line.iloc[-1]
                and macd_line.iloc[-2] <= signal_line.iloc[-2]
            )
        else:
            is_bullish_cross = False

        return {
            "macd_line": float(macd_val),
            "signal_line": float(signal_val),
            "histogram": float(hist_val),
            "is_bullish_cross": is_bullish_cross,
        }

    @staticmethod
    def compute_bollinger(
        df: pd.DataFrame, period: int = 20, std_dev: float = 2.0
    ) -> dict:
        """
        Compute Bollinger Bands.

        Args:
            df: DataFrame with 'close' column
            period: Moving average period (default 20)
            std_dev: Standard deviation multiplier (default 2.0)

        Returns:
            dict with keys: upper, mid, lower, bandwidth, percent_b
        """
        close = df["close"]

        # Mid band (SMA)
        mid = close.rolling(window=period).mean()

        # Standard deviation
        std = close.rolling(window=period).std()

        # Upper and lower bands
        upper = mid + (std * std_dev)
        lower = mid - (std * std_dev)

        # Get latest values
        upper_val = upper.iloc[-1]
        mid_val = mid.iloc[-1]
        lower_val = lower.iloc[-1]
        close_val = close.iloc[-1]

        # Bandwidth = (upper - lower) / mid
        bandwidth = (upper_val - lower_val) / mid_val if mid_val != 0 else np.nan

        # Percent B = (close - lower) / (upper - lower)
        if upper_val != lower_val:
            percent_b = (close_val - lower_val) / (upper_val - lower_val)
        else:
            percent_b = np.nan

        return {
            "upper": float(upper_val),
            "mid": float(mid_val),
            "lower": float(lower_val),
            "bandwidth": float(bandwidth),
            "percent_b": float(percent_b),
        }

    @staticmethod
    def compute_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """
        Compute Exponential Moving Average.

        Args:
            df: DataFrame with 'close' column
            period: EMA period

        Returns:
            pd.Series with EMA values
        """
        return df["close"].ewm(span=period, adjust=False).mean()

    @staticmethod
    def compute_adx(df: pd.DataFrame, period: int = 14) -> float:
        """
        Compute Average Directional Index (ADX).

        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ADX period (default 14)

        Returns:
            Latest ADX value (float)
        """
        TAAnalyzer._validate_columns(df, ["high", "low", "close"])
        high, low, close = df["high"], df["low"], df["close"]
        tr = TAAnalyzer._compute_tr(df)

        # Calculate Directional Movement
        up_move = high.diff()
        down_move = -low.diff()

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

        # Smooth with EMA (Wilder's smoothing)
        alpha = 1.0 / period

        atr = tr.ewm(alpha=alpha, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=alpha, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=alpha, adjust=False).mean() / atr)

        # Calculate DX (guard against division by zero)
        di_sum = plus_di + minus_di
        dx = 100 * abs(plus_di - minus_di) / di_sum.where(di_sum > 0, np.nan)

        # ADX is the EMA of DX
        adx = dx.ewm(alpha=alpha, adjust=False).mean()

        return float(adx.iloc[-1])

    @staticmethod
    def compute_atr(df: pd.DataFrame, period: int = 14) -> float:
        """
        Compute Average True Range (ATR).

        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ATR period (default 14)

        Returns:
            Latest ATR value (float)
        """
        TAAnalyzer._validate_columns(df, ["high", "low", "close"])
        tr = TAAnalyzer._compute_tr(df)

        # Calculate ATR using Wilder's smoothing (EMA with alpha = 1/period)
        alpha = 1.0 / period
        atr = tr.ewm(alpha=alpha, adjust=False).mean()

        return float(atr.iloc[-1])

    @staticmethod
    def compute_all(df: pd.DataFrame) -> dict:
        """Compute all technical indicators with NaN-safe composite score."""
        min_rows = 50
        if len(df) < min_rows:
            raise ValueError(
                f"DataFrame has {len(df)} rows, need at least {min_rows} "
                f"for reliable indicator computation"
            )

        rsi_series = TAAnalyzer.compute_rsi(df, period=14)
        rsi_14 = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0

        macd = TAAnalyzer.compute_macd(df)
        bb = TAAnalyzer.compute_bollinger(df)

        ema_9 = float(TAAnalyzer.compute_ema(df, period=9).iloc[-1])
        ema_21 = float(TAAnalyzer.compute_ema(df, period=21).iloc[-1])
        ema_50 = float(TAAnalyzer.compute_ema(df, period=50).iloc[-1])

        adx_14 = TAAnalyzer.compute_adx(df, period=14)
        atr_14 = TAAnalyzer.compute_atr(df, period=14)

        close = float(df["close"].iloc[-1])

        composite_score = rsi_14 * 0.4
        composite_score += 20 if macd.get("is_bullish_cross", False) else 0
        percent_b = bb.get("percent_b", 0.5)
        composite_score += (percent_b if not (isinstance(percent_b, float) and pd.isna(percent_b)) else 0.5) * 20
        composite_score += 20 if not pd.isna(close) and not pd.isna(ema_21) and close > ema_21 else 0

        if pd.isna(composite_score):
            composite_score = 50.0
        composite_score = max(0.0, min(100.0, composite_score))

        return {
            "rsi_14": rsi_14,
            "macd": macd,
            "bb": bb,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "ema_50": ema_50,
            "adx_14": adx_14,
            "atr_14": atr_14,
            "composite_score": composite_score,
        }
