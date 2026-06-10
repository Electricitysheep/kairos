"""Tests for the RiskAgent."""

from __future__ import annotations

import pytest

from kairos.agents.base import AgentContext
from kairos.agents.risk import RiskAgent


@pytest.mark.asyncio
async def test_name_property():
    """Test that name property returns 'risk'."""
    agent = RiskAgent()
    assert agent.name == "risk"


@pytest.mark.asyncio
async def test_default_demo_mode():
    """Test default demo mode returns expected output keys."""
    agent = RiskAgent()
    context = AgentContext(input_data={})
    result = await agent.process(context)

    expected_keys = {
        "var_95",
        "var_99",
        "cvar_95",
        "kelly_fraction",
        "max_position",
        "kelly_position",
        "portfolio_value",
        "circuit_breaker_active",
        "is_safe",
    }
    assert expected_keys.issubset(result.output.keys())


@pytest.mark.asyncio
async def test_var_values_are_negative():
    """Test VaR 95 and VaR 99 values are negative (risk is measured as loss)."""
    agent = RiskAgent()
    context = AgentContext(
        input_data={
            "returns": [-0.01, -0.02, -0.03, -0.04, -0.05, 0.01, 0.02, 0.03]
        }
    )
    result = await agent.process(context)

    assert result.output["var_95"] < 0
    assert result.output["var_99"] < 0


@pytest.mark.asyncio
async def test_kelly_fraction_in_range():
    """Test Kelly fraction is between 0 and 0.5."""
    agent = RiskAgent()
    context = AgentContext(
        input_data={"win_rate": 0.6, "avg_win": 0.06, "avg_loss": 0.03}
    )
    result = await agent.process(context)

    kelly_fraction = result.output["kelly_fraction"]
    assert 0.0 <= kelly_fraction <= 0.5


@pytest.mark.asyncio
async def test_circuit_breaker_makes_unsafe():
    """Test circuit breaker active makes is_safe = False."""
    agent = RiskAgent()
    context = AgentContext(
        input_data={"circuit_breaker": True, "returns": [-0.01] * 10}
    )
    result = await agent.process(context)

    assert result.output["circuit_breaker_active"] is True
    assert result.output["is_safe"] is False


@pytest.mark.asyncio
async def test_max_position_within_portfolio():
    """Test max_position <= portfolio_value."""
    agent = RiskAgent()
    context = AgentContext(
        input_data={"portfolio_value": 10000.0}, config={"max_position_pct": 0.1}
    )
    result = await agent.process(context)

    assert result.output["max_position"] <= result.output["portfolio_value"]


@pytest.mark.asyncio
async def test_zero_loss_kelly_fraction():
    """Test win rate of 0 with no avg_loss gives kelly_fraction=0."""
    agent = RiskAgent()
    context = AgentContext(
        input_data={"win_rate": 0.0, "avg_win": 0.0, "avg_loss": 0.0}
    )
    result = await agent.process(context)

    assert result.output["kelly_fraction"] == 0.0