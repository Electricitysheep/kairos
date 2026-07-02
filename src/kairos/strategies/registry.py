"""Strategy registry — supports both dict configs and custom Strategy classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kairos.strategies.base import Strategy


@dataclass
class StrategyConfig:
    """Configuration for a trading strategy (dict-based, backward compat)."""

    name: str
    description: str
    agent_config: dict


class StrategyRegistry:
    """Registry of available trading strategies.

    Supports two types of strategies:
    1. Dict-based (StrategyConfig) — simple threshold configs, used by CLI
    2. Class-based (Strategy subclass) — custom Python logic, plugin system
    """

    def __init__(self):
        self._configs: dict[str, StrategyConfig] = {}
        self._classes: dict[str, type[Strategy]] = {}
        self._load_builtins()

    def _load_builtins(self) -> None:
        from kairos.strategies.builtin import BUILTIN_CONFIGS, BUILTIN_STRATEGIES

        self._configs.update(BUILTIN_CONFIGS)
        self._classes.update(BUILTIN_STRATEGIES)

    def names(self) -> list[str]:
        return list(self._configs.keys())

    def get(self, name: str) -> StrategyConfig:
        if name not in self._configs:
            raise KeyError(f"Unknown strategy: {name}. Available: {list(self._configs.keys())}")
        return self._configs[name]

    def get_class(self, name: str) -> type[Strategy]:
        """Get a Strategy class by name. Raises KeyError if not found."""
        if name not in self._classes:
            raise KeyError(f"No Strategy class for: {name}. Available: {list(self._classes.keys())}")
        return self._classes[name]

    def register(self, config: StrategyConfig) -> None:
        self._configs[config.name] = config

    def register_class(
        self,
        name: str,
        strategy_class: type[Strategy],
        description: str = "",
        agent_config: dict | None = None,
    ) -> None:
        """Register a custom Strategy subclass.

        Example:
            class MyStrategy(Strategy): ...
            registry.register_class("my_strat", MyStrategy,
                                    description="My custom strategy")
        """
        self._classes[name] = strategy_class
        cfg = StrategyConfig(
            name=name,
            description=description or strategy_class.__doc__ or "",
            agent_config=agent_config or {},
        )
        self._configs[name] = cfg

    def get_all(self) -> list[StrategyConfig]:
        return list(self._configs.values())
