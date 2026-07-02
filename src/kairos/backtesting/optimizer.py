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

    def optimize(self, param_grid: dict[str, list[Any]]) -> list[dict]:
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
