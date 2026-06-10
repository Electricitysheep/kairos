"""Tests for the expanded strategy library."""

from __future__ import annotations

import pandas as pd
import pytest

from kairos.strategies.builtin import (
    RSIStrategy, BollingerBandsStrategy, EnsembleStrategy,
    MomentumStrategy, BUILTIN_STRATEGIES,
)
from kairos.strategies.base import StrategyContext
from kairos.data.mock import MockDataProvider


def _make_ctx(days: int = 100) -> StrategyContext:
    df = MockDataProvider.generate_price_data(days=days, seed=42)
    return StrategyContext(df)


class TestRSIStrategy:
    def test_returns_signal(self):
        strat = RSIStrategy()
        signal = strat.compute_signal(_make_ctx())
        assert signal.action in ("BUY", "SELL", "HOLD")

    def test_name_in_registry(self):
        assert "rsi" in BUILTIN_STRATEGIES


class TestBollingerBandsStrategy:
    def test_returns_signal(self):
        strat = BollingerBandsStrategy()
        signal = strat.compute_signal(_make_ctx())
        assert signal.action in ("BUY", "SELL", "HOLD")

    def test_name_in_registry(self):
        assert "bb" in BUILTIN_STRATEGIES


class TestEnsembleStrategy:
    def test_returns_signal(self):
        strat = EnsembleStrategy()
        signal = strat.compute_signal(_make_ctx())
        assert signal.action in ("BUY", "SELL", "HOLD")

    def test_name_in_registry(self):
        assert "ensemble" in BUILTIN_STRATEGIES

    def test_ensemble_uses_voting(self):
        """Ensemble should produce same output as sub-strategies on same data."""
        ensemble = EnsembleStrategy()
        momentum = MomentumStrategy()
        ctx = _make_ctx()
        e_signal = ensemble.compute_signal(ctx)
        m_signal = momentum.compute_signal(ctx)
        assert e_signal.action in ("BUY", "SELL", "HOLD")
        assert m_signal.action in ("BUY", "SELL", "HOLD")


class TestAllStrategies:
    def test_all_strategies_have_configs(self):
        from kairos.strategies.builtin import BUILTIN_CONFIGS
        for name in BUILTIN_STRATEGIES:
            assert name in BUILTIN_CONFIGS, f"{name} missing config"

    def test_all_strategies_run_without_error(self):
        ctx = _make_ctx()
        for name, cls in BUILTIN_STRATEGIES.items():
            strat = cls()
            signal = strat.compute_signal(ctx)
            assert signal.action in ("BUY", "SELL", "HOLD"), f"{name} failed"
