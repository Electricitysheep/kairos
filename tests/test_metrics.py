"""Tests for PerformanceMetrics."""

from __future__ import annotations

import numpy as np
import pytest

from kairos.backtesting.metrics import PerformanceMetrics


class TestPerformanceMetrics:
    def test_constant_returns(self):
        m = PerformanceMetrics([0.01] * 100)
        assert m.win_rate == 1.0
        assert m.max_drawdown == 0.0

    def test_cumulative_return_positive(self):
        m = PerformanceMetrics([0.05, 0.03, -0.02])
        assert m.cumulative_return == pytest.approx((1.05 * 1.03 * 0.98) - 1, rel=1e-4)

    def test_cumulative_return_negative(self):
        m = PerformanceMetrics([-0.05] * 10)
        assert m.cumulative_return < 0

    def test_sharpe_ratio_zero_vol(self):
        m = PerformanceMetrics([0.0] * 10)
        assert m.sharpe_ratio == 0.0

    def test_sharpe_ratio_positive(self):
        np.random.seed(42)
        returns = list(np.random.normal(0.001, 0.02, 500))
        m = PerformanceMetrics(returns)
        assert m.sharpe_ratio != 0.0

    def test_max_drawdown(self):
        m = PerformanceMetrics([0.1, -0.2, 0.1])
        dd = m.max_drawdown
        assert dd > 0

    def test_max_drawdown_zero(self):
        m = PerformanceMetrics([0.01] * 50)
        assert m.max_drawdown == 0.0

    def test_win_rate(self):
        m = PerformanceMetrics([0.01, 0.02, -0.01, 0.03, -0.02])
        assert m.win_rate == pytest.approx(0.6, rel=1e-2)

    def test_profit_factor(self):
        m = PerformanceMetrics([0.1, 0.2, -0.05, -0.05, 0.3])
        pf = m.profit_factor
        assert pf > 0

    def test_profit_factor_all_losses(self):
        m = PerformanceMetrics([-0.01, -0.02])
        assert m.profit_factor == 0.0

    def test_empty_returns(self):
        m = PerformanceMetrics([])
        d = m.compute_all()
        assert d["cumulative_return"] == 0.0
        assert d["n_returns"] == 0

    def test_compute_all_keys(self):
        m = PerformanceMetrics([0.01, -0.005, 0.02])
        d = m.compute_all()
        expected = {"cumulative_return", "annualized_return", "annualized_volatility",
                    "sharpe_ratio", "max_drawdown", "win_rate", "profit_factor", "n_returns"}
        assert set(d.keys()) == expected
