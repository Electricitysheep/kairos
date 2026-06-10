"""Tests for QuantAgent."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from kairos.agents.quant import QuantAgent
from kairos.agents.base import AgentContext


def make_trend_data(n=100, trend="up"):
    """
    Create synthetic OHLCV data with a specified trend.

    Args:
        n: Number of periods
        trend: 'up', 'down', or 'sideways'

    Returns:
        pd.DataFrame with open, high, low, close, volume columns
    """
    np.random.seed(42)
    close = np.zeros(n)
    close[0] = 100
    for i in range(1, n):
        # Stronger drift for clearer trend signals
        drift = 0.005 if trend == "up" else (-0.005 if trend == "down" else 0)
        noise = 0.01 if trend == "sideways" else 0.005
        close[i] = close[i - 1] * (1 + np.random.normal(drift, noise))
    df = pd.DataFrame({"close": close})
    df["high"] = df["close"] * (1 + abs(np.random.normal(0, 0.005, n)))
    df["low"] = df["close"] * (1 - abs(np.random.normal(0, 0.005, n)))
    df["open"] = df["close"].shift(1).fillna(df["close"].iloc[0])
    df["volume"] = np.random.uniform(1000, 5000, n)
    return df


class TestQuantAgentName:
    """Tests for QuantAgent name property."""

    def test_name_property_returns_quant(self):
        """Name property should return 'quant'."""
        agent = QuantAgent()
        assert agent.name == "quant"


class TestQuantAgentProcess:
    """Tests for QuantAgent.process method."""

    @pytest.mark.asyncio
    async def test_process_returns_expected_output_keys(self):
        """Process should return output dict with all expected keys."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        expected_keys = {
            "rsi_14",
            "macd",
            "bb",
            "ema_9",
            "ema_21",
            "ema_50",
            "adx_14",
            "atr_14",
            "composite_score",
            "signal",
            "signal_strength",
        }
        assert set(result.output.keys()) == expected_keys, (
            f"Output should have keys {expected_keys}, got {set(result.output.keys())}"
        )

    @pytest.mark.asyncio
    async def test_composite_score_between_0_and_100(self):
        """Composite score should be between 0 and 100."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        assert 0 <= result.output["composite_score"] <= 100, (
            f"Composite score should be between 0 and 100, got {result.output['composite_score']}"
        )

    @pytest.mark.asyncio
    async def test_signal_is_one_of_valid_values(self):
        """Signal should be one of 'bullish', 'bearish', or 'neutral'."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="sideways")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        valid_signals = {"bullish", "bearish", "neutral"}
        assert result.output["signal"] in valid_signals, (
            f"Signal should be one of {valid_signals}, got {result.output['signal']}"
        )

    @pytest.mark.asyncio
    async def test_bullish_data_produces_bullish_signal(self):
        """Uptrend data should produce a bullish signal."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        # In uptrend with RSI > 55, composite score should be high
        # so we expect bullish signal
        assert result.output["signal"] == "bullish", (
            f"Uptrend should produce bullish signal, got {result.output['signal']}"
        )

    @pytest.mark.asyncio
    async def test_bearish_data_produces_bearish_signal(self):
        """Downtrend data should produce a bearish signal."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="down")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        # In downtrend, composite score should be low
        # so we expect bearish signal
        assert result.output["signal"] == "bearish", (
            f"Downtrend should produce bearish signal, got {result.output['signal']}"
        )

    @pytest.mark.asyncio
    async def test_result_confidence_is_valid(self):
        """AgentResult confidence should be between 0 and 1."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        assert 0 <= result.confidence <= 1, (
            f"Confidence should be between 0 and 1, got {result.confidence}"
        )

    @pytest.mark.asyncio
    async def test_result_confidence_matches_composite_score(self):
        """Confidence should be composite_score / 100."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        expected_confidence = result.output["composite_score"] / 100.0
        assert abs(result.confidence - expected_confidence) < 0.001, (
            f"Confidence should be composite_score / 100 = {expected_confidence}, got {result.confidence}"
        )

    @pytest.mark.asyncio
    async def test_result_has_valid_agent_name(self):
        """AgentResult agent_name should be 'quant'."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        assert result.agent_name == "quant", (
            f"agent_name should be 'quant', got {result.agent_name}"
        )

    @pytest.mark.asyncio
    async def test_result_has_reasoning(self):
        """AgentResult should have a non-empty reasoning string."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        assert len(result.reasoning) > 0, "Reasoning should not be empty"

    @pytest.mark.asyncio
    async def test_signal_strength_is_valid(self):
        """Signal strength should be one of 'strong', 'moderate', or 'weak'."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        valid_strengths = {"strong", "moderate", "weak"}
        assert result.output["signal_strength"] in valid_strengths, (
            f"Signal strength should be one of {valid_strengths}, got {result.output['signal_strength']}"
        )

    @pytest.mark.asyncio
    async def test_macd_output_has_expected_keys(self):
        """MACD output should have keys: macd_line, signal_line, histogram, is_bullish_cross."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        macd_keys = {"macd_line", "signal_line", "histogram", "is_bullish_cross"}
        assert set(result.output["macd"].keys()) == macd_keys, (
            f"MACD should have keys {macd_keys}, got {set(result.output['macd'].keys())}"
        )

    @pytest.mark.asyncio
    async def test_bb_output_has_expected_keys(self):
        """BB output should have keys: upper, mid, lower, bandwidth, percent_b."""
        agent = QuantAgent()
        df = make_trend_data(n=100, trend="up")
        context = AgentContext(input_data={"ohlcv": df})
        result = await agent.process(context)

        bb_keys = {"upper", "mid", "lower", "bandwidth", "percent_b"}
        assert set(result.output["bb"].keys()) == bb_keys, (
            f"BB should have keys {bb_keys}, got {set(result.output['bb'].keys())}"
        )

    @pytest.mark.asyncio
    async def test_generates_mock_data_when_no_ohlcv_provided(self):
        """Agent should generate mock data when no ohlcv is provided in context."""
        agent = QuantAgent()
        context = AgentContext(input_data={})
        result = await agent.process(context)

        # Should still produce valid output with mock data
        assert "rsi_14" in result.output
        assert "composite_score" in result.output
        assert "signal" in result.output