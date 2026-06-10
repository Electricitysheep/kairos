"""Tests for ResearchAgent."""

from __future__ import annotations

import pytest

from kairos.agents.base import AgentContext
from kairos.agents.research import ResearchAgent


@pytest.mark.asyncio
async def test_research_agent_name_property():
    agent = ResearchAgent()
    assert agent.name == "research"


@pytest.mark.asyncio
async def test_demo_mode_returns_expected_keys():
    context = AgentContext(input_data={"mode": "demo", "token": "SOL/USDT", "seed": 42})
    agent = ResearchAgent()
    result = await agent.process(context)

    assert result.agent_name == "research"
    assert "token" in result.output
    assert "price_data" in result.output
    assert "volume_data" in result.output
    assert "ohlcv" in result.output


@pytest.mark.asyncio
async def test_demo_mode_confidence_greater_than_zero():
    context = AgentContext(input_data={"mode": "demo", "token": "SOL/USDT", "seed": 42})
    agent = ResearchAgent()
    result = await agent.process(context)

    assert result.confidence > 0


@pytest.mark.asyncio
async def test_agent_result_has_research_agent_name():
    context = AgentContext(input_data={"mode": "demo", "token": "BTC/USDT", "seed": 123})
    agent = ResearchAgent()
    result = await agent.process(context)

    assert result.agent_name == "research"


@pytest.mark.asyncio
async def test_different_tokens_produce_different_results():
    context1 = AgentContext(input_data={"mode": "demo", "token": "SOL/USDT", "seed": 42})
    context2 = AgentContext(input_data={"mode": "demo", "token": "BTC/USDT", "seed": 42})

    agent = ResearchAgent()
    result1 = await agent.process(context1)
    result2 = await agent.process(context2)

    # Different tokens should produce different token values in output
    assert result1.output["token"] == "SOL/USDT"
    assert result2.output["token"] == "BTC/USDT"
    assert result1.output["token"] != result2.output["token"]


@pytest.mark.asyncio
async def test_demo_mode_contains_technical_summary():
    context = AgentContext(input_data={"mode": "demo", "token": "SOL/USDT", "seed": 42})
    agent = ResearchAgent()
    result = await agent.process(context)

    assert "technical_summary" in result.output
    assert isinstance(result.output["technical_summary"], str)
    assert len(result.output["technical_summary"]) > 0


@pytest.mark.asyncio
async def test_demo_mode_contains_data_quality():
    context = AgentContext(input_data={"mode": "demo", "token": "SOL/USDT", "seed": 42})
    agent = ResearchAgent()
    result = await agent.process(context)

    assert "data_quality" in result.output
    assert result.output["data_quality"] in ["excellent", "good", "fair"]


@pytest.mark.asyncio
async def test_live_mode_returns_error():
    context = AgentContext(input_data={"mode": "live", "token": "SOL/USDT"})
    agent = ResearchAgent()
    result = await agent.process(context)

    assert result.confidence == 0.0
    assert "error" in result.output
    assert "DataProvider" in result.output["error"]