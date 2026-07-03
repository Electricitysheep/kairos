"""Notification primitives: the alert payload and the Notifier interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

_DECISION_EMOJI = {"BUY": "\U0001f7e2", "SELL": "\U0001f534", "HOLD": "⚪"}


@dataclass
class TradeAlert:
    """A single trading alert to be delivered by a :class:`Notifier`."""

    token: str
    decision: str
    confidence: float = 0.0
    reason: str = ""

    def format(self) -> str:
        """Render the alert as a human-readable message."""
        decision = self.decision.upper()
        emoji = _DECISION_EMOJI.get(decision, "•")
        text = f"{emoji} {decision} {self.token} — confidence {self.confidence:.0%}"
        if self.reason:
            text += f"\n{self.reason}"
        return text


class Notifier(ABC):
    """Abstract delivery channel for :class:`TradeAlert` messages."""

    @abstractmethod
    async def send(self, alert: TradeAlert) -> bool:
        """Deliver an alert. Returns True on success."""


class MultiNotifier(Notifier):
    """Fan an alert out to several notifiers; succeeds only if all succeed."""

    def __init__(self, notifiers: Iterable[Notifier]) -> None:
        self._notifiers = list(notifiers)

    async def send(self, alert: TradeAlert) -> bool:
        results = [await notifier.send(alert) for notifier in self._notifiers]
        return all(results)
