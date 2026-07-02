"""Strategy base class — write custom strategies as Python classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass
class Signal:
    """Trading signal produced by a Strategy."""

    action: str  # "BUY", "SELL", "HOLD"
    confidence: float = 0.5
    reason: str = ""

    @classmethod
    def buy(cls, confidence: float = 0.6, reason: str = "") -> "Signal":
        return cls(action="BUY", confidence=confidence, reason=reason)

    @classmethod
    def sell(cls, confidence: float = 0.6, reason: str = "") -> "Signal":
        return cls(action="SELL", confidence=confidence, reason=reason)

    @classmethod
    def hold(cls, reason: str = "") -> "Signal":
        return cls(action="HOLD", confidence=0.5, reason=reason)


class StrategyContext:
    """Provides market data and indicators to a strategy during evaluation."""

    def __init__(self, data: pd.DataFrame, config: dict | None = None):
        self._data = data
        self.config = config or {}

    @property
    def prices(self) -> pd.Series:
        return self._data["close"] if "close" in self._data else pd.Series(dtype=float)

    @property
    def volume(self) -> pd.Series:
        return self._data["volume"] if "volume" in self._data else pd.Series(dtype=float)

    def latest(self, column: str = "close") -> float:
        return float(self._data[column].iloc[-1]) if column in self._data and len(self._data) > 0 else 0.0


class Strategy(ABC):
    """Base class for all trading strategies.

    Subclass this to create your own strategy:

        class MyStrategy(Strategy):
            def compute_signal(self, ctx: StrategyContext) -> Signal:
                price = ctx.latest()
                if price > ctx.config.get("threshold", 100):
                    return Signal.buy(reason=f"Price {price} above threshold")
                return Signal.hold()
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def compute_signal(self, ctx: StrategyContext) -> Signal:
        """Compute a trading signal from market data and indicators.

        Args:
            ctx: StrategyContext with prices, volume, and config.

        Returns:
            Signal with action, confidence, and reasoning.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.name}(config={self.config})"
