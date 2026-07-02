"""Simulated portfolio for walk-forward backtesting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Trade:
    """A single simulated trade."""

    timestamp: str
    action: str  # "BUY" or "SELL"
    price: float
    shares: float
    value: float
    reason: str = ""


@dataclass
class PortfolioSnapshot:
    """Portfolio state at a point in time."""

    timestamp: str
    cash: float
    shares: float
    position_value: float
    total_value: float


class SimulatedPortfolio:
    """Tracks a simulated trading portfolio during backtesting.

    Starts with initial_cash. Tracks:
    - Cash balance
    - Shares held
    - Position value (shares * current_price)
    - Total value (cash + position_value)
    - Trade history
    - P&L
    """

    def __init__(self, initial_cash: float = 10000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.shares: float = 0.0
        self.trades: list[Trade] = []
        self.snapshots: list[PortfolioSnapshot] = []
        self._current_price: float | None = None
        self._timestamp: str = ""

    def update_price(self, price: float, timestamp: str | None = None) -> None:
        """Update current price and record snapshot."""
        self._current_price = price
        self._timestamp = timestamp if timestamp is not None else ""
        self.snapshots.append(
            PortfolioSnapshot(
                timestamp=self._timestamp,
                cash=self.cash,
                shares=self.shares,
                position_value=self.position_value,
                total_value=self.total_value,
            )
        )

    def execute_trade(
        self,
        action: str,
        price: float,
        value: float | None = None,
        reason: str = "",
        timestamp: str | None = None,
    ) -> float:
        """Execute a trade at the given price.

        Args:
            action: "BUY" or "SELL" or "HOLD"
            price: Execution price
            value: USD amount to trade (for BUY). If None, uses cash * 0.95.
            reason: Reason for the trade
            timestamp: Optional timestamp for the trade

        Returns:
            Actual shares traded (BUY returns shares, SELL/HOLD returns 0)
        """
        ts = timestamp if timestamp is not None else self._timestamp
        action_upper = action.upper()

        if action_upper == "BUY":
            # Determine how much to spend (default to 95% of cash)
            spend = value if value is not None else self.cash * 0.95
            # Cap at available cash
            spend = min(spend, self.cash)
            # Calculate shares
            shares_traded = spend / price if price > 0 else 0.0
            cost = shares_traded * price
            self.shares += shares_traded
            self.cash -= cost
            self.trades.append(
                Trade(
                    timestamp=ts,
                    action="BUY",
                    price=price,
                    shares=shares_traded,
                    value=cost,
                    reason=reason,
                )
            )
            return shares_traded

        elif action_upper == "SELL":
            if self.shares > 0:
                requested = value if value is not None else self.shares * price
                shares_to_sell = min(self.shares, requested / price) if price > 0 else 0
                actual_value = shares_to_sell * price
                self.cash += actual_value
                self.shares = max(0.0, self.shares - shares_to_sell)
                self.trades.append(
                    Trade(
                        timestamp=ts,
                        action="SELL",
                        price=price,
                        shares=shares_to_sell,
                        value=actual_value,
                        reason=reason,
                    )
                )
            return 0.0

        # HOLD or unknown action
        return 0.0

    @property
    def position_value(self) -> float:
        return self.shares * (self._current_price or 0.0)

    @property
    def total_value(self) -> float:
        return self.cash + self.position_value

    @property
    def total_return(self) -> float:
        """Return as percentage (e.g., 0.15 for 15%)."""
        if self.initial_cash == 0:
            return 0.0
        return (self.total_value - self.initial_cash) / self.initial_cash

    def get_returns_series(self) -> list[float]:
        """Return list of periodic returns from snapshots."""
        if len(self.snapshots) < 2:
            return []
        returns = []
        for i in range(1, len(self.snapshots)):
            prev = self.snapshots[i - 1].total_value
            curr = self.snapshots[i].total_value
            if prev != 0:
                returns.append((curr - prev) / prev)
        return returns

    def get_summary(self) -> dict:
        """Return summary dict:
        - initial_cash, final_value, total_return
        - trade_count, win_count, loss_count
        - win_rate
        - max_drawdown (from snapshot values)
        """
        sell_trades = [t for t in self.trades if t.action == "SELL"]

        # Track win/loss by comparing sell value to cost basis
        # A sell is a "win" if it recovers more than the initial investment portion
        win_count = 0
        loss_count = 0

        # Simplified: track cumulative cost basis and compare to cumulative proceeds
        total_cost = 0.0
        total_proceeds = 0.0
        for t in self.trades:
            if t.action == "BUY":
                total_cost += t.value
            elif t.action == "SELL":
                total_proceeds += t.value

        # Count wins/losses from sell trades (compare each sell to buy cost of those shares)
        # Use a per-round tracking approach: when we sell, we had a prior buy
        # For simplicity, a sell that exceeds the proportional buy cost is a win
        buy_cost = 0.0
        buy_shares = 0.0
        for t in self.trades:
            if t.action == "BUY":
                buy_cost += t.value
                buy_shares += t.shares
            elif t.action == "SELL":
                if buy_shares > 0:
                    # Proportional cost basis for these shares
                    cost_basis = buy_cost * (t.shares / buy_shares)
                    if t.value > cost_basis:
                        win_count += 1
                    elif t.value < cost_basis:
                        loss_count += 1
                    # Recalculate remaining buy state
                    buy_cost -= cost_basis
                    buy_shares -= t.shares

        trade_count = len(sell_trades)
        win_rate = win_count / trade_count if trade_count > 0 else 0.0

        # Max drawdown from snapshots
        max_dd = 0.0
        peak = self.initial_cash
        if self.snapshots:
            peak = self.snapshots[0].total_value
        for snap in self.snapshots:
            if snap.total_value > peak:
                peak = snap.total_value
            dd = (peak - snap.total_value) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        return {
            "initial_cash": self.initial_cash,
            "final_value": round(self.total_value, 2),
            "total_return": round(self.total_return, 4),
            "trade_count": trade_count,
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": round(win_rate, 4),
            "max_drawdown": round(max_dd, 4),
        }
