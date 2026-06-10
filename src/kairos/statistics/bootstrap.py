"""Bootstrap significance tests for backtest results."""

from __future__ import annotations

import numpy as np


class BootstrapSignificanceTest:
    """Test statistical significance of backtest performance using bootstrap.

    Tests the null hypothesis that the strategy's Sharpe ratio is zero
    by resampling returns with replacement and computing two-sided p-value.
    """

    def __init__(self, returns: list[float], n_iterations: int = 1000, seed: int = 42):
        if len(returns) < 10:
            raise ValueError(f"Need at least 10 returns, got {len(returns)}")
        self.returns = np.array(returns, dtype=float)
        self.n_iterations = n_iterations
        self.seed = seed

    def run(self) -> dict:
        observed_sharpe = self._compute_sharpe(self.returns)
        rng = np.random.default_rng(self.seed)
        boot_sharpes = np.zeros(self.n_iterations)

        for i in range(self.n_iterations):
            resampled = rng.choice(self.returns, size=len(self.returns), replace=True)
            boot_sharpes[i] = self._compute_sharpe(resampled)

        lower = float(np.percentile(boot_sharpes, 2.5))
        upper = float(np.percentile(boot_sharpes, 97.5))
        if lower > upper:
            lower, upper = upper, lower

        # Two-sided p-value: fraction of bootstrap samples with |sharpe| >= |observed|
        p_value = float(np.mean(np.abs(boot_sharpes) >= np.abs(observed_sharpe)))

        return {
            "sharpe_observed": round(float(observed_sharpe), 4),
            "sharpe_ci_95": (round(lower, 4), round(upper, 4)),
            "p_value": round(p_value, 4),
            "is_significant": p_value < 0.05,
            "n_iterations": self.n_iterations,
        }

    @staticmethod
    def _compute_sharpe(returns: np.ndarray) -> float:
        if len(returns) < 2:
            return 0.0
        mean = float(returns.mean())
        std = float(returns.std(ddof=1))
        if std == 0:
            return 0.0
        return mean / std * float(np.sqrt(365))
