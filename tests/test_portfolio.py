"""Tests for SimulatedPortfolio."""

from __future__ import annotations

import pytest

from kairos.backtesting.portfolio import SimulatedPortfolio


class TestSimulatedPortfolio:
    def test_initial_state(self):
        """cash=10000, shares=0, total_value=10000."""
        p = SimulatedPortfolio()
        assert p.cash == 10000.0
        assert p.shares == 0.0
        assert p.total_value == 10000.0

    def test_buy_reduces_cash(self):
        """BUY $1000 at $100 → cash=9000, shares=10."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=1000.0)
        assert p.cash == pytest.approx(9000.0)
        assert p.shares == pytest.approx(10.0)

    def test_sell_increases_cash(self):
        """BUY then SELL → cash back to initial."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=5000.0)  # buy 50 shares
        initial_cash = p.cash
        p.update_price(105.0)
        p.execute_trade("SELL", 105.0)  # sell all 50 shares at $105
        expected = initial_cash + 50 * 105.0
        assert p.cash == pytest.approx(expected)
        assert p.shares == 0.0

    def test_hold_does_nothing(self):
        """HOLD → no change."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        result = p.execute_trade("HOLD", 100.0)
        assert result == 0.0
        assert p.cash == 10000.0
        assert p.shares == 0.0
        assert len(p.trades) == 0

    def test_update_price_affects_value(self):
        """BUY then price doubles → position value doubles."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=5000.0)  # 50 shares
        assert p.position_value == pytest.approx(5000.0)
        p.update_price(200.0)
        assert p.position_value == pytest.approx(10000.0)

    def test_total_return_on_gain(self):
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=5000.0)
        p.update_price(110.0)
        p.execute_trade("SELL", 110.0)
        assert p.cash == pytest.approx(10500.0, rel=1e-3)
        assert p.total_return > 0

    def test_trade_history(self):
        """Trades recorded correctly."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=1000.0, reason="test_buy")
        assert len(p.trades) == 1
        assert p.trades[0].action == "BUY"
        assert p.trades[0].price == 100.0
        assert p.trades[0].shares == 10.0
        assert p.trades[0].value == 1000.0
        assert p.trades[0].reason == "test_buy"

    def test_get_summary(self):
        """Summary dict has expected keys."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=5000.0)
        p.update_price(110.0)
        p.execute_trade("SELL", 110.0)
        summary = p.get_summary()
        assert "initial_cash" in summary
        assert "final_value" in summary
        assert "total_return" in summary
        assert "trade_count" in summary
        assert "win_count" in summary
        assert "loss_count" in summary
        assert "win_rate" in summary
        assert "max_drawdown" in summary

    def test_multiple_trades(self):
        """Multiple BUY/SELL cycles work."""
        p = SimulatedPortfolio()
        # Cycle 1: buy low, sell high
        p.update_price(95.0)
        p.execute_trade("BUY", 95.0, value=5000.0)
        p.update_price(105.0)
        p.execute_trade("SELL", 105.0)
        # Cycle 2: buy again
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=3000.0)
        p.update_price(115.0)
        p.execute_trade("SELL", 115.0)
        summary = p.get_summary()
        assert summary["trade_count"] == 2
        assert len(p.snapshots) > 0

    def test_max_drawdown_in_summary(self):
        p = SimulatedPortfolio(initial_cash=10000)
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=8000.0)
        p.update_price(120.0)
        p.update_price(80.0)
        p.update_price(100.0)
        summary = p.get_summary()
        assert summary["max_drawdown"] > 0.0
        assert summary["max_drawdown"] < 1.0

    def test_execute_trade_returns_shares_traded(self):
        """execute_trade returns actual shares traded."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        shares = p.execute_trade("BUY", 100.0, value=1000.0)
        assert shares == 10.0

    def test_execute_trade_sell_returns_zero(self):
        """execute_trade SELL returns 0 (shares set to 0)."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.execute_trade("BUY", 100.0, value=5000.0)
        result = p.execute_trade("SELL", 110.0)
        assert result == 0.0
        assert p.shares == 0.0

    def test_snapshots_recorded_on_price_update(self):
        """Snapshots are recorded each time update_price is called."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        p.update_price(105.0)
        p.update_price(110.0)
        assert len(p.snapshots) == 3

    def test_snapshot_fields(self):
        """Snapshot contains correct fields."""
        p = SimulatedPortfolio()
        p.update_price(100.0)
        snap = p.snapshots[0]
        assert snap.cash == 10000.0
        assert snap.shares == 0.0
        assert snap.position_value == 0.0
        assert snap.total_value == 10000.0
