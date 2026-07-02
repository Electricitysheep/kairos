"""Kairos — AI Trading Agents, Fully Transparent & Verifiable."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from kairos.__version__ import __version__

if TYPE_CHECKING:
    from kairos.core.orchestrator import Orchestrator
    from kairos.strategies.base import Signal, Strategy, StrategyContext

__all__ = ["__version__", "Orchestrator", "Signal", "Strategy", "StrategyContext"]

# Map of public names to (module, attribute) resolved lazily on first access so
# that ``import kairos`` stays lightweight (no pandas/agent imports up front).
_LAZY_EXPORTS = {
    "Orchestrator": ("kairos.core.orchestrator", "Orchestrator"),
    "Signal": ("kairos.strategies.base", "Signal"),
    "Strategy": ("kairos.strategies.base", "Strategy"),
    "StrategyContext": ("kairos.strategies.base", "StrategyContext"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'kairos' has no attribute {name!r}")
    module, attr = target
    return getattr(importlib.import_module(module), attr)


def __dir__() -> list[str]:
    return sorted(__all__)
