"""Multi-timeframe analysis — combine signals from 15m, 1h, 1d timeframes."""

from __future__ import annotations

import pandas as pd

from kairos.indicators.ta import TAAnalyzer


def resample_ohlcv(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Resample OHLCV data to a different frequency."""
    if df.empty:
        return df
    resampled = df.resample(freq).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })
    resampled = resampled.dropna(subset=["open", "close"])
    return resampled


def compute_multi_timeframe_score(df: pd.DataFrame) -> dict:
    """Compute composite scores for 15min, 1h, and 1d timeframes.
    
    Returns a dict with individual scores and a blended score.
    The blended score gives more weight to higher timeframes.
    """
    scores = {}
    weights = {}
    
    # Determine available data span
    if len(df) < 10:
        return {"score_15m": 50, "score_1h": 50, "score_1d": 50,
                "blended": 50, "timeframes_available": 0}
    
    # 15-minute (use raw data if freq is already ~15min or higher)
    if len(df) >= 50:
        try:
            ind = TAAnalyzer.compute_all(df)
            scores["15m"] = ind["composite_score"]
            weights["15m"] = 0.2
        except Exception:
            scores["15m"] = 50
            weights["15m"] = 0.2
    else:
        scores["15m"] = 50
        weights["15m"] = 0.2
    
    # 1-hour
    if len(df) >= 100:
        try:
            df_1h = resample_ohlcv(df, "1h")
            if len(df_1h) >= 50:
                ind = TAAnalyzer.compute_all(df_1h)
                scores["1h"] = ind["composite_score"]
                weights["1h"] = 0.3
            else:
                scores["1h"] = scores["15m"]
                weights["1h"] = 0.3
        except Exception:
            scores["1h"] = scores["15m"]
            weights["1h"] = 0.3
    else:
        scores["1h"] = scores["15m"]
        weights["1h"] = 0.3
    
    # 1-day
    if len(df) >= 500:
        try:
            df_1d = resample_ohlcv(df, "1D")
            if len(df_1d) >= 50:
                ind = TAAnalyzer.compute_all(df_1d)
                scores["1d"] = ind["composite_score"]
                weights["1d"] = 0.5
            else:
                scores["1d"] = scores["1h"]
                weights["1d"] = 0.5
        except Exception:
            scores["1d"] = scores["1h"]
            weights["1d"] = 0.5
    else:
        scores["1d"] = scores["1h"]
        weights["1d"] = 0.5
    
    blended = sum(scores[k] * weights[k] for k in scores)
    
    return {
        "score_15m": round(scores.get("15m", 50), 1),
        "score_1h": round(scores.get("1h", 50), 1),
        "score_1d": round(scores.get("1d", 50), 1),
        "blended": round(blended, 1),
        "timeframes_available": len(scores),
    }
