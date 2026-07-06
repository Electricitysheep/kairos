"""Bootstrap significance tests for backtest results."""

from __future__ import annotations

import numpy as np


class BootstrapSignificanceTest:
    """Test statistical significance of backtest performance using bootstrap.

    Tests the null hypothesis that the strategy's Sharpe ratio is zero
    by resampling returns with replacement and computing two-sided p-value.
    """

    def __init__(
        self,
        returns: list[float],
        n_iterations: int = 1000,
        seed: int = 42,
        periods_per_year: int = 365,
    ):
        if len(returns) < 10:
            raise ValueError(f"Need at least 10 returns, got {len(returns)}")
        self.returns = np.array(returns, dtype=float)
        self.n_iterations = n_iterations
        self.seed = seed
        self.periods_per_year = periods_per_year

    def run(self) -> dict:
        observed_sharpe = self._compute_sharpe(self.returns, self.periods_per_year)
        rng = np.random.default_rng(self.seed)
        n = len(self.returns)

        # Null hypothesis: true mean return is zero. Demean the returns so the
        # resampled Sharpe distribution is centred at zero; resampling the raw
        # returns instead would centre it on the observed Sharpe and force
        # p ~= 0.5 regardless of the strategy.
        null_returns = self.returns - self.returns.mean()

        boot_sharpes = np.zeros(self.n_iterations)  # estimator distribution (CI)
        null_sharpes = np.zeros(self.n_iterations)  # H0 distribution (p-value)

        for i in range(self.n_iterations):
            idx = rng.integers(0, n, size=n)
            boot_sharpes[i] = self._compute_sharpe(self.returns[idx], self.periods_per_year)
            null_sharpes[i] = self._compute_sharpe(null_returns[idx], self.periods_per_year)

        lower = float(np.percentile(boot_sharpes, 2.5))
        upper = float(np.percentile(boot_sharpes, 97.5))
        if lower > upper:
            lower, upper = upper, lower

        # Two-sided p-value under H0: fraction of null-distribution Sharpes at
        # least as extreme as the observed one.
        p_value = float(np.mean(np.abs(null_sharpes) >= np.abs(observed_sharpe)))

        return {
            "sharpe_observed": round(float(observed_sharpe), 4),
            "sharpe_ci_95": (round(lower, 4), round(upper, 4)),
            "p_value": round(p_value, 4),
            "is_significant": p_value < 0.05,
            "n_iterations": self.n_iterations,
            "periods_per_year": self.periods_per_year,
        }

    @staticmethod
    def _compute_sharpe(returns: np.ndarray, periods_per_year: int = 365) -> float:
        if len(returns) < 2:
            return 0.0
        mean = float(returns.mean())
        std = float(returns.std(ddof=1))
        if std == 0:
            return 0.0
        return mean / std * float(np.sqrt(periods_per_year))
