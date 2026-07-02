"""Example: Write and use a custom Strategy Plugin.

Run: python examples/custom_strategy.py
"""

from __future__ import annotations

import pandas as pd

from kairos.strategies.base import Strategy, StrategyContext, Signal
from kairos.strategies.registry import StrategyRegistry
from kairos.data.mock import MockDataProvider
from kairos.backtesting.engine import WalkForwardEngine


class DualMAStrategy(Strategy):
    """Simple dual moving average crossover strategy.
    
    Buys when fast MA crosses above slow MA, sells when crosses below.
    Shows how to write a custom strategy with arbitrary logic.
    """

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        prices = ctx.prices
        if len(prices) < 50:
            return Signal.hold(reason="Not enough data")

        fast_period = self.config.get("fast_period", 10)
        slow_period = self.config.get("slow_period", 30)

        fast_ma = prices.rolling(window=fast_period).mean()
        slow_ma = prices.rolling(window=slow_period).mean()

        if pd.isna(fast_ma.iloc[-1]) or pd.isna(slow_ma.iloc[-1]):
            return Signal.hold(reason="Computing MAs...")

        if fast_ma.iloc[-2] <= slow_ma.iloc[-2] and fast_ma.iloc[-1] > slow_ma.iloc[-1]:
            return Signal.buy(confidence=0.65,
                              reason=f"Fast MA({fast_period}) crossed above Slow MA({slow_period})")
        elif fast_ma.iloc[-2] >= slow_ma.iloc[-2] and fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            return Signal.sell(confidence=0.6,
                               reason=f"Fast MA({fast_period}) crossed below Slow MA({slow_period})")
        return Signal.hold(reason="No crossover")


def main():
    # 1. Register the custom strategy
    registry = StrategyRegistry()
    registry.register_class(
        "dual_ma", DualMAStrategy,
        description="Dual moving average crossover strategy",
        agent_config={"fast_period": 10, "slow_period": 30},
    )
    print(f"Registered strategies: {registry.names()}")

    # 2. Use it like any built-in strategy
    cfg = registry.get("dual_ma")
    print(f"Using: {cfg.name} — {cfg.description}")

    # 3. Backtest it
    df = MockDataProvider.generate_price_data(days=365, seed=42)
    engine = WalkForwardEngine(df, train_size=90, test_size=30)
    result = engine.run(cfg.agent_config)
    agg = result["aggregate"]
    print(f"\nBacktest Results:")
    print(f"  Return: {agg['cumulative_return']:.2%}")
    print(f"  Sharpe: {agg['sharpe_ratio']:.2f}")
    print(f"  Max DD: {agg['max_drawdown']:.2%}")

    # 4. Or use it directly for analysis
    strat = DualMAStrategy(config={"fast_period": 10, "slow_period": 30})
    ctx = StrategyContext(df)
    signal = strat.compute_signal(ctx)
    print(f"\nLatest Signal: {signal.action} (confidence: {signal.confidence:.0%})")
    print(f"  Reason: {signal.reason}")


if __name__ == "__main__":
    main()
