"""Tests for the Strategy Plugin System."""

from __future__ import annotations

import pandas as pd
import pytest

from kairos.strategies.base import Strategy, StrategyContext, Signal
from kairos.strategies.registry import StrategyRegistry


class TestStrategyBase:
    def test_signal_buy_factory(self):
        s = Signal.buy(confidence=0.8, reason="test")
        assert s.action == "BUY"
        assert s.confidence == 0.8
        assert s.reason == "test"

    def test_signal_sell_factory(self):
        s = Signal.sell(confidence=0.7)
        assert s.action == "SELL"
        assert s.confidence == 0.7

    def test_signal_hold_factory(self):
        s = Signal.hold()
        assert s.action == "HOLD"

    def test_custom_strategy(self):
        class AlwaysBuy(Strategy):
            def compute_signal(self, ctx: StrategyContext) -> Signal:
                return Signal.buy(reason="Always buy strategy")

        strat = AlwaysBuy()
        ctx = StrategyContext(pd.DataFrame({"close": [100, 101, 102]}))
        result = strat.compute_signal(ctx)
        assert result.action == "BUY"
        assert result.reason == "Always buy strategy"

    def test_custom_strategy_with_config(self):
        class ThresholdStrategy(Strategy):
            def compute_signal(self, ctx: StrategyContext) -> Signal:
                threshold = self.config.get("threshold", 100)
                if ctx.latest() > threshold:
                    return Signal.buy(reason=f"Price {ctx.latest():.0f} > {threshold}")
                return Signal.hold()

        strat = ThresholdStrategy(config={"threshold": 101})
        ctx = StrategyContext(pd.DataFrame({"close": [100, 102]}))
        result = strat.compute_signal(ctx)
        assert result.action == "BUY"


class TestStrategyRegistry:
    def test_register_custom_class(self):
        class CustomStrat(Strategy):
            def compute_signal(self, ctx: StrategyContext) -> Signal:
                return Signal.hold()

        registry = StrategyRegistry()
        registry.register_class("custom", CustomStrat, description="Custom test")
        assert "custom" in registry.names()
        cls = registry.get_class("custom")
        assert cls is CustomStrat

    def test_use_custom_strategy(self):
        class MeanCrossStrategy(Strategy):
            def compute_signal(self, ctx: StrategyContext) -> Signal:
                prices = ctx.prices
                if len(prices) < 2:
                    return Signal.hold()
                if prices.iloc[-1] > prices.iloc[-2]:
                    return Signal.buy(confidence=0.6, reason="Price increasing")
                return Signal.sell(confidence=0.5, reason="Price decreasing")

        strat = MeanCrossStrategy()
        ctx = StrategyContext(pd.DataFrame({"close": [100, 101, 102]}))
        result = strat.compute_signal(ctx)
        assert result.action == "BUY"
