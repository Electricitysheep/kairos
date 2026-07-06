"""Tests for BootstrapSignificanceTest."""

from __future__ import annotations

import numpy as np
import pytest

from kairos.statistics.bootstrap import BootstrapSignificanceTest


class TestBootstrapSignificanceTest:
    def test_insufficient_returns_raises(self):
        with pytest.raises(ValueError, match="at least 10"):
            BootstrapSignificanceTest([0.01] * 3)

    def test_run_returns_dict(self):
        returns = list(np.random.normal(0.001, 0.02, 100))
        bst = BootstrapSignificanceTest(returns, n_iterations=50, seed=42)
        result = bst.run()
        assert "sharpe_observed" in result
        assert "sharpe_ci_95" in result
        assert "p_value" in result
        assert "is_significant" in result
        assert "n_iterations" in result

    def test_ci_is_tuple(self):
        returns = list(np.random.normal(0.001, 0.02, 200))
        bst = BootstrapSignificanceTest(returns, n_iterations=50, seed=42)
        result = bst.run()
        lower, upper = result["sharpe_ci_95"]
        assert lower <= upper

    def test_deterministic_seed(self):
        returns = list(np.random.normal(0.001, 0.02, 200))
        r1 = BootstrapSignificanceTest(returns, n_iterations=50, seed=123).run()
        r2 = BootstrapSignificanceTest(returns, n_iterations=50, seed=123).run()
        assert r1["sharpe_observed"] == r2["sharpe_observed"]

    def test_n_iterations_recorded(self):
        returns = list(np.random.normal(0.001, 0.02, 100))
        bst = BootstrapSignificanceTest(returns, n_iterations=100, seed=42)
        assert bst.run()["n_iterations"] == 100


class TestStatisticalValidity:
    """The p-value must come from a proper null distribution (mean-zero returns).

    Regression: resampling *raw* returns centres the bootstrap distribution on
    the observed Sharpe, so p is approximately 0.5 for every strategy and
    nothing is ever significant.
    """

    def test_strong_edge_is_significant(self):
        rng = np.random.default_rng(0)
        # Daily Sharpe ~2 -- an edge this strong over 100 days must be detected.
        returns = list(rng.normal(0.01, 0.005, 100))
        result = BootstrapSignificanceTest(returns, n_iterations=1000, seed=42).run()
        assert result["p_value"] < 0.05, (
            f"p={result['p_value']} for an overwhelming edge -- "
            "null distribution is not centred at zero"
        )
        assert result["is_significant"] is True

    def test_pure_noise_is_not_significant(self):
        rng = np.random.default_rng(1)
        returns = list(rng.normal(0.0, 0.02, 200))
        result = BootstrapSignificanceTest(returns, n_iterations=1000, seed=42).run()
        assert result["p_value"] > 0.05
        assert result["is_significant"] is False

    def test_periods_per_year_configurable(self):
        rng = np.random.default_rng(2)
        returns = list(rng.normal(0.002, 0.01, 120))
        crypto = BootstrapSignificanceTest(returns, n_iterations=50, seed=42, periods_per_year=365).run()
        stocks = BootstrapSignificanceTest(returns, n_iterations=50, seed=42, periods_per_year=252).run()
        ratio = crypto["sharpe_observed"] / stocks["sharpe_observed"]
        assert ratio == pytest.approx(np.sqrt(365 / 252), rel=1e-3)
