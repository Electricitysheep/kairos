"""Tests for StrategyOptimizer."""

from __future__ import annotations

from kairos.backtesting.optimizer import StrategyOptimizer
from kairos.data.mock import MockDataProvider


class TestStrategyOptimizer:
    def test_optimize_returns_results(self):
        df = MockDataProvider.generate_price_data(days=200, seed=42)
        opt = StrategyOptimizer(df, train_size=60, test_size=20)
        results = opt.optimize({"buy_threshold": [60, 70]})
        assert len(results) == 2
        assert results[0]["sharpe"] >= results[1]["sharpe"]

    def test_results_have_expected_keys(self):
        df = MockDataProvider.generate_price_data(days=200, seed=42)
        opt = StrategyOptimizer(df, train_size=60, test_size=20)
        results = opt.optimize({"buy_threshold": [60]})
        r = results[0]
        assert "params" in r
        assert "sharpe" in r
        assert "return" in r
        assert "max_drawdown" in r
