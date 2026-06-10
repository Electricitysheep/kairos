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
