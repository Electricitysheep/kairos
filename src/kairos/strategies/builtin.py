"""Built-in rule-based strategies using the new Strategy API."""

from __future__ import annotations

import pandas as pd

from kairos.strategies.registry import StrategyConfig as _StrategyConfig

from kairos.strategies.base import Strategy, StrategyContext, Signal
from kairos.indicators.ta import TAAnalyzer


class MomentumStrategy(Strategy):
    """Trend-following: buy when composite score > threshold."""

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        indicators = TAAnalyzer.compute_all(ctx._data)
        score = indicators["composite_score"]
        buy_at = self.config.get("buy_threshold", 65)
        sell_at = self.config.get("sell_threshold", 35)

        if score > buy_at:
            return Signal.buy(confidence=min(1.0, score / 100),
                              reason=f"Composite score {score:.0f} above {buy_at}")
        elif score < sell_at:
            return Signal.sell(confidence=min(1.0, (100 - score) / 100),
                               reason=f"Composite score {score:.0f} below {sell_at}")
        return Signal.hold(reason=f"Score {score:.0f} in neutral zone [{sell_at}, {buy_at}]")


class RSIStrategy(Strategy):
    """RSI mean reversion: buys when oversold (<30), sells when overbought (>70)."""

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        indicators = TAAnalyzer.compute_all(ctx._data)
        rsi = indicators.get("rsi_14", 50)
        oversold = self.config.get("oversold", 30)
        overbought = self.config.get("overbought", 70)

        if rsi < oversold:
            return Signal.buy(confidence=max(0.5, 1.0 - rsi / 100),
                              reason=f"RSI {rsi:.0f} below {oversold} (oversold)")
        elif rsi > overbought:
            return Signal.sell(confidence=max(0.5, rsi / 100),
                               reason=f"RSI {rsi:.0f} above {overbought} (overbought)")
        return Signal.hold(reason=f"RSI {rsi:.0f} in neutral zone [{oversold}, {overbought}]")


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands breakout: buys on close above upper band (momentum)."""

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        indicators = TAAnalyzer.compute_all(ctx._data)
        bb = indicators.get("bb", {})
        percent_b = bb.get("percent_b", 0.5)

        if pd.isna(percent_b):
            return Signal.hold(reason="BB data not available")

        if percent_b > self.config.get("buy_level", 0.9):
            return Signal.buy(confidence=min(1.0, percent_b),
                              reason=f"PercentB {percent_b:.2f} > {self.config.get('buy_level', 0.9)} (breakout)")
        elif percent_b < self.config.get("sell_level", 0.1):
            return Signal.sell(confidence=min(1.0, 1.0 - percent_b),
                               reason=f"PercentB {percent_b:.2f} < {self.config.get('sell_level', 0.1)} (breakdown)")
        return Signal.hold(reason=f"PercentB {percent_b:.2f} in range [{self.config.get('sell_level', 0.1)}, {self.config.get('buy_level', 0.9)}]")


class EnsembleStrategy(Strategy):
    """Ensemble: combines signals from multiple sub-strategies via majority vote."""

    def __init__(self, config=None):
        super().__init__(config)
        self._sub_strategies = [
            MomentumStrategy(config),
            RSIStrategy(config),
            BollingerBandsStrategy(config),
        ]

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        votes: dict[str, float] = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
        total_conf = 0.0

        for strat in self._sub_strategies:
            try:
                signal = strat.compute_signal(ctx)
                votes[signal.action] = votes.get(signal.action, 0) + signal.confidence
                total_conf += 1
            except Exception:
                pass

        if total_conf == 0:
            return Signal.hold(reason="No sub-strategies available")

        winner = max(votes, key=votes.get)
        avg_conf = votes[winner] / total_conf
        if winner == "BUY":
            return Signal.buy(confidence=avg_conf,
                              reason=f"Ensemble vote: {votes['BUY']:.1f} buy, {votes['SELL']:.1f} sell, {votes['HOLD']:.1f} hold")
        elif winner == "SELL":
            return Signal.sell(confidence=avg_conf,
                               reason=f"Ensemble vote: {votes['BUY']:.1f} buy, {votes['SELL']:.1f} sell, {votes['HOLD']:.1f} hold")
        return Signal.hold(reason=f"Ensemble vote: {votes['BUY']:.1f} buy, {votes['SELL']:.1f} sell, {votes['HOLD']:.1f} hold")


class MeanReversionStrategy(Strategy):
    """Mean reversion: buy on dips when score recovers above threshold."""

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        indicators = TAAnalyzer.compute_all(ctx._data)
        score = indicators["composite_score"]

        if score > self.config.get("buy_threshold", 50):
            return Signal.buy(confidence=min(1.0, score / 100),
                              reason=f"Score {score:.0f} recovered above buy threshold")
        elif score < self.config.get("sell_threshold", 40):
            return Signal.sell(confidence=min(1.0, (100 - score) / 100),
                               reason=f"Score {score:.0f} dropped below sell threshold")
        return Signal.hold(reason=f"Score {score:.0f} in neutral zone")


class ConservativeStrategy(Strategy):
    """Conservative: only buys at very high conviction with tight risk."""

    def compute_signal(self, ctx: StrategyContext) -> Signal:
        indicators = TAAnalyzer.compute_all(ctx._data)
        score = indicators["composite_score"]
        rsi = indicators.get("rsi_14", 50)

        if score > self.config.get("buy_threshold", 75) and rsi < 80:
            return Signal.buy(confidence=0.6,
                              reason=f"High conviction: score {score:.0f}, RSI {rsi:.0f}")
        elif score < self.config.get("sell_threshold", 30):
            return Signal.sell(confidence=0.5,
                               reason=f"Score {score:.0f} below exit threshold")
        return Signal.hold(reason=f"Score {score:.0f} below conviction threshold")


# Registry of built-in strategy classes
BUILTIN_STRATEGIES: dict[str, type[Strategy]] = {
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "conservative": ConservativeStrategy,
    "rsi": RSIStrategy,
    "bb": BollingerBandsStrategy,
    "ensemble": EnsembleStrategy,
}

# Dict configs for backward compatibility with CLI
BUILTIN_CONFIGS: dict[str, _StrategyConfig] = {}  # populated below

BUILTIN_CONFIGS.update({
    "momentum": _StrategyConfig(name="momentum",
        description="Trend-following. Buys on strong momentum signals.",
        agent_config={"buy_threshold": 65, "sell_threshold": 35}),
    "mean_reversion": _StrategyConfig(name="mean_reversion",
        description="Mean reversion. Buys on dips with recovery signals.",
        agent_config={"buy_threshold": 50, "sell_threshold": 40}),
    "conservative": _StrategyConfig(name="conservative",
        description="Conservative. High conviction entries with tight risk.",
        agent_config={"buy_threshold": 75, "sell_threshold": 30, "max_position_pct": 0.05}),
    "rsi": _StrategyConfig(name="rsi",
        description="RSI mean reversion. Buys when oversold (<30), sells when overbought (>70).",
        agent_config={}),
    "bb": _StrategyConfig(name="bb",
        description="Bollinger Bands breakout. Buys on close above upper band (momentum).",
        agent_config={}),
    "ensemble": _StrategyConfig(name="ensemble",
        description="Ensemble. Combines signals from momentum, RSI, and BB strategies.",
        agent_config={}),
})
