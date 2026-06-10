"""Tests for WalkForwardEngine."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from kairos.backtesting.engine import WalkForwardEngine
from kairos.data.mock import MockDataProvider


def _make_data(n_days: int = 200) -> pd.DataFrame:
    return MockDataProvider.generate_price_data(days=n_days, seed=42)


class TestWalkForwardEngine:
    def test_requires_ohlcv_columns(self):
        bad_df = pd.DataFrame({"a": [1, 2, 3]})
        with pytest.raises(ValueError, match="columns"):
            WalkForwardEngine(bad_df)

    def test_insufficient_data_raises(self):
        df = _make_data(n_days=5)
        with pytest.raises(ValueError, match="Insufficient"):
            WalkForwardEngine(df, train_size=100, test_size=50)

    def test_run_returns_dict(self):
        df = _make_data(n_days=200)
        engine = WalkForwardEngine(df, train_size=60, test_size=20, step_size=20)
        result = engine.run()
        assert isinstance(result, dict)
        assert "aggregate" in result
        assert "all_returns" in result
        assert "n_windows" in result

    def test_aggregate_has_all_keys(self):
        df = _make_data(n_days=200)
        engine = WalkForwardEngine(df, train_size=60, test_size=20, step_size=20)
        result = engine.run()
        agg = result["aggregate"]
        expected = {"cumulative_return", "annualized_return", "annualized_volatility",
                    "sharpe_ratio", "max_drawdown", "win_rate", "profit_factor", "n_returns"}
        assert set(agg.keys()) == expected

    def test_strategy_config_passed_through(self):
        df = _make_data(n_days=200)
        engine = WalkForwardEngine(df, train_size=60, test_size=20, step_size=20)
        custom_config = {"buy_threshold": 80}
        result = engine.run(strategy_config=custom_config)
        assert result["strategy_config"]["buy_threshold"] == 80

    def test_multiple_windows(self):
        df = _make_data(n_days=300)
        engine = WalkForwardEngine(df, train_size=60, test_size=20, step_size=30)
        result = engine.run()
        assert result["n_windows"] >= 3

    def test_returns_not_empty(self):
        df = _make_data(n_days=250)
        engine = WalkForwardEngine(df, train_size=60, test_size=20, step_size=30)
        result = engine.run()
        assert len(result["all_returns"]) > 0
