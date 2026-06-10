"""Performance metrics calculator for backtesting."""

from __future__ import annotations

import numpy as np


class PerformanceMetrics:
    """Compute performance metrics from a series of returns."""

    def __init__(self, returns: list[float], risk_free_rate: float = 0.0):
        self.returns = np.array(returns, dtype=float)
        self.risk_free_rate = risk_free_rate

    @property
    def cumulative_return(self) -> float:
        if len(self.returns) == 0:
            return 0.0
        return float(np.prod(1 + self.returns) - 1)

    @property
    def annualized_return(self) -> float:
        if len(self.returns) == 0:
            return 0.0
        total = self.cumulative_return
        n_years = len(self.returns) / 365
        if n_years <= 0:
            return 0.0
        return float((1 + total) ** (1 / n_years) - 1)

    @property
    def annualized_volatility(self) -> float:
        if len(self.returns) < 2:
            return 0.0
        return float(self.returns.std(ddof=1) * np.sqrt(365))

    @property
    def sharpe_ratio(self) -> float:
        vol = self.annualized_volatility
        if vol == 0:
            return 0.0
        return (self.annualized_return - self.risk_free_rate) / vol

    @property
    def max_drawdown(self) -> float:
        if len(self.returns) == 0:
            return 0.0
        cumulative = np.cumprod(1 + self.returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        return float(abs(drawdowns.min()))

    @property
    def win_rate(self) -> float:
        if len(self.returns) == 0:
            return 0.0
        return float(np.mean(self.returns > 0))

    @property
    def profit_factor(self) -> float:
        gains = self.returns[self.returns > 0].sum()
        losses = abs(self.returns[self.returns < 0].sum())
        if losses == 0:
            return float("inf") if gains > 0 else 0.0
        return float(gains / losses)

    def compute_all(self) -> dict:
        return {
            "cumulative_return": round(self.cumulative_return, 4),
            "annualized_return": round(self.annualized_return, 4),
            "annualized_volatility": round(self.annualized_volatility, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "win_rate": round(self.win_rate, 4),
            "profit_factor": (
                round(self.profit_factor, 4)
                if self.profit_factor != float("inf") and self.profit_factor != float("-inf")
                else None
            ),
            "n_returns": len(self.returns),
        }
