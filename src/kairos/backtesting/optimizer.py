"""Strategy parameter optimizer — grid search with walk-forward validation."""

from __future__ import annotations

import itertools
from typing import Any

import pandas as pd

from kairos.backtesting.engine import WalkForwardEngine


class StrategyOptimizer:
    """Grid search optimizer for strategy parameters.

    Tests all combinations of parameters via walk-forward backtesting
    and returns results ranked by Sharpe ratio.

    Example:
        optimizer = StrategyOptimizer(data, train_size=90, test_size=30)
        results = optimizer.optimize({
            "buy_threshold": [60, 65, 70],
            "sell_threshold": [30, 35, 40],
        })
        best = results[0]  # Best params by Sharpe
    """

    def __init__(self, data: pd.DataFrame, train_size: int = 90, test_size: int = 30, progress_callback=None):
        self.data = data
        self.train_size = train_size
        self.test_size = test_size
        self.progress_callback = progress_callback

    def optimize_walk_forward(self, param_grid: dict[str, list[Any]]) -> dict:
        """Per-window walk-forward optimization (the methodologically sound path).

        For every walk-forward window, parameters are grid-searched on the
        TRAIN slice only (ranked by Sharpe) and then applied out-of-sample
        to the TEST slice. Returns the engine result, including
        "window_params" (the parameters chosen per window) and "aggregate"
        (metrics over the pooled out-of-sample returns).
        """
        engine = WalkForwardEngine(
            self.data,
            train_size=self.train_size,
            test_size=self.test_size,
        )
        return engine.run(param_grid=param_grid, progress_callback=self.progress_callback)

    def optimize(self, param_grid: dict[str, list[Any]]) -> list[dict]:
        """Rank parameter combinations by pooled out-of-sample Sharpe.

        WARNING: picking parameters from this ranking reuses the test
        windows for selection (data snooping), so the top entry's Sharpe is
        an optimistic estimate. Use optimize_walk_forward() when parameters
        must be chosen on train data only.
        """
        keys = list(param_grid.keys())
        combinations = list(itertools.product(*param_grid.values()))
        results = []
        total = len(combinations)

        for i, combo in enumerate(combinations):
            params = dict(zip(keys, combo))
            engine = WalkForwardEngine(
                self.data,
                train_size=self.train_size,
                test_size=self.test_size,
            )
            result = engine.run(params)
            agg = result["aggregate"]
            results.append(
                {
                    "params": params,
                    "sharpe": agg["sharpe_ratio"],
                    "return": agg["cumulative_return"],
                    "max_drawdown": agg["max_drawdown"],
                    "win_rate": agg["win_rate"],
                }
            )
            if self.progress_callback:
                self.progress_callback(i + 1, total)

        results.sort(key=lambda r: r["sharpe"], reverse=True)
        return results
