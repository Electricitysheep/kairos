"""Walk-forward per-window optimization: train windows must actually train.

Spec: when a param_grid is supplied, each window's parameters are selected
by grid search on that window's TRAIN slice only, then applied to the
corresponding TEST slice. Previously the train slices were never used and
the optimizer ranked parameters on pooled out-of-sample returns
(selection on test data).
"""

import itertools

import numpy as np
import pandas as pd
import pytest

from kairos.backtesting.engine import WalkForwardEngine
from kairos.backtesting.metrics import PerformanceMetrics
from kairos.backtesting.optimizer import StrategyOptimizer
from kairos.backtesting.splitter import WalkForwardSplitter

GRID = {"buy_threshold": [55, 70], "sell_threshold": [30, 45]}


def make_ohlcv(n: int = 300, seed: int = 3) -> pd.DataFrame:
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


def grid_combos(grid: dict) -> list[dict]:
    return [dict(zip(grid.keys(), c)) for c in itertools.product(*grid.values())]


class TestPerWindowOptimization:
    def test_window_params_selected_by_train_sharpe(self):
        """Chosen params per window == argmax Sharpe over the TRAIN slice."""
        data = make_ohlcv()
        engine = WalkForwardEngine(data, train_size=90, test_size=30)
        result = engine.run(param_grid=GRID)

        windows = WalkForwardSplitter(
            n_samples=len(data), train_size=90, test_size=30, step_size=30, embargo=5
        ).split()
        assert len(result["window_params"]) == len(windows)

        for wp, window in zip(result["window_params"], windows):
            expected_params, expected_sharpe = None, float("-inf")
            for params in grid_combos(GRID):
                returns = engine._run_range(window.train_start, window.train_end, params)
                sharpe = PerformanceMetrics(returns).compute_all()["sharpe_ratio"]
                if sharpe > expected_sharpe:
                    expected_sharpe, expected_params = sharpe, params
            assert wp["params"] == expected_params, (
                f"{window.name}: selected {wp['params']} but train-slice argmax "
                f"is {expected_params} — selection is not driven by train data"
            )
            assert wp["params"] in grid_combos(GRID)

    def test_run_without_param_grid_is_unchanged(self):
        data = make_ohlcv()
        engine = WalkForwardEngine(data, train_size=90, test_size=30)
        result = engine.run()
        assert "window_params" not in result

    def test_param_grid_rejected_in_agent_mode(self):
        """Agents are built once from a fixed config; per-window sweeps
        would silently not take effect, so they must be rejected."""
        from kairos.agents.quant import QuantAgent

        data = make_ohlcv()
        engine = WalkForwardEngine(data, train_size=90, test_size=30, quant_agent=QuantAgent({}))
        with pytest.raises(ValueError, match="classic"):
            engine.run(param_grid=GRID)

    def test_optimizer_walk_forward_delegates(self):
        data = make_ohlcv()
        optimizer = StrategyOptimizer(data, train_size=90, test_size=30)
        result = optimizer.optimize_walk_forward(GRID)
        assert "window_params" in result
        assert "aggregate" in result
        assert len(result["window_params"]) >= 1
