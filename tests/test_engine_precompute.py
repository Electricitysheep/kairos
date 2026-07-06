"""Regression tests: precomputed indicators must be causal (no look-ahead).

Guards against the bug where compute_macd()/compute_bollinger() scalars
(derived from the *last* bar of the full dataset) were broadcast to every
row of the precomputed indicator frame.
"""

import numpy as np
import pandas as pd
import pytest

from kairos.backtesting.engine import WalkForwardEngine


def make_ohlcv(n: int = 200, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    return pd.DataFrame(
        {
            "open": close * (1 + rng.normal(0, 0.001, n)),
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": rng.uniform(1e5, 1e6, n),
        }
    )


def precompute(data: pd.DataFrame) -> pd.DataFrame:
    engine = WalkForwardEngine(data, train_size=90, test_size=30)
    return engine._precompute_indicators()


PER_BAR_COLUMNS = ["macd_histogram", "macd_bullish", "bb_percent_b", "bb_upper", "bb_lower"]


class TestPrecomputedIndicatorsAreCausal:
    def test_indicator_columns_vary_over_time(self):
        """A per-bar indicator on a 200-bar random walk cannot be constant."""
        pre = precompute(make_ohlcv())
        for col in ["macd_histogram", "macd_bullish", "bb_percent_b"]:
            n_unique = pre[col].dropna().nunique()
            assert n_unique > 1, (
                f"{col} has {n_unique} unique value(s) over 200 bars — "
                "full-sample scalar broadcast to every row (look-ahead)"
            )

    def test_values_do_not_depend_on_future_bars(self):
        """Indicator at bar i must be identical whether or not bars > i exist."""
        data = make_ohlcv()
        cut = 150
        full = precompute(data)
        prefix = precompute(data.iloc[:cut].reset_index(drop=True))
        for col in PER_BAR_COLUMNS:
            left = pd.Series(np.asarray(full[col].iloc[:cut], dtype=float))
            right = pd.Series(np.asarray(prefix[col], dtype=float))
            pd.testing.assert_series_equal(
                left, right, check_names=False, atol=1e-10, rtol=1e-10,
                obj=f"{col} (bars 0..{cut - 1} changed when future bars were appended)",
            )

    def test_composite_score_varies_across_bars(self):
        """Composite score should differ across bars once indicators are per-bar."""
        data = make_ohlcv()
        engine = WalkForwardEngine(data, train_size=90, test_size=30)
        pre = engine._precompute_indicators()
        scores = {
            round(engine._composite_from_precomputed(pre.iloc[i]), 6)
            for i in range(100, 190)
        }
        assert len(scores) > 1, "composite score is flat — indicator inputs are constants"
