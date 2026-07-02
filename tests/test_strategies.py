"""Tests for StrategyRegistry."""

from __future__ import annotations

import pytest

from kairos.strategies.registry import StrategyRegistry, StrategyConfig


class TestStrategyRegistry:
    def test_registry_has_builtins(self):
        r = StrategyRegistry()
        names = r.names()
        assert "momentum" in names
        assert "mean_reversion" in names
        assert "conservative" in names

    def test_get_returns_config(self):
        r = StrategyRegistry()
        cfg = r.get("momentum")
        assert cfg.name == "momentum"
        assert "buy_threshold" in cfg.agent_config

    def test_get_unknown_raises(self):
        r = StrategyRegistry()
        with pytest.raises(KeyError, match="unknown_strategy"):
            r.get("unknown_strategy")

    def test_register_custom(self):
        r = StrategyRegistry()
        custom = StrategyConfig(
            name="custom_test",
            description="Test strategy",
            agent_config={"buy_threshold": 50, "sell_threshold": 50},
        )
        r.register(custom)
        assert "custom_test" in r.names()
        assert r.get("custom_test").name == "custom_test"

    def test_get_all_returns_all(self):
        r = StrategyRegistry()
        all_cfgs = r.get_all()
        assert len(all_cfgs) >= 3
        assert all(isinstance(c, StrategyConfig) for c in all_cfgs)

    def test_momentum_config(self):
        r = StrategyRegistry()
        m = r.get("momentum")
        assert m.agent_config["buy_threshold"] == 65
        assert m.agent_config["sell_threshold"] == 35

    def test_conservative_config(self):
        r = StrategyRegistry()
        c = r.get("conservative")
        assert c.agent_config["max_position_pct"] == 0.05
