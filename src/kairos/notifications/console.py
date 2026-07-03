"""Console notifier — prints alerts to stdout (or an injected printer)."""

from __future__ import annotations

from typing import Callable

from kairos.notifications.base import Notifier, TradeAlert


class ConsoleNotifier(Notifier):
    """Print alerts locally. The printer is injectable for testing."""

    def __init__(self, printer: Callable[[str], None] = print) -> None:
        self._print = printer

    async def send(self, alert: TradeAlert) -> bool:
        self._print(alert.format())
        return True
