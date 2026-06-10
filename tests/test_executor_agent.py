"""Tests for ExecutorAgent."""

from __future__ import annotations

import pytest

from kairos.agents.base import AgentContext
from kairos.agents.executor import ExecutorAgent
from kairos.core.journal import DecisionJournal


@pytest.mark.asyncio
async def test_name_property_returns_executor():
    agent = ExecutorAgent()
    assert agent.name == "executor"


@pytest.mark.asyncio
async def test_high_composite_score_produces_buy():
    agent = ExecutorAgent()
    ctx = AgentContext(
        input_data={
            "quant_output": {"composite_score": 80},
            "risk_output": {"is_safe": True, "circuit_breaker_active": False},
        }
    )
    result = await agent.process(ctx)
    assert result.output["decision"] == "BUY"
    assert result.agent_name == "executor"


@pytest.mark.asyncio
async def test_low_composite_score_produces_sell():
    agent = ExecutorAgent(config={"enable_sell": True})
    ctx = AgentContext(
        input_data={
            "quant_output": {"composite_score": 20},
            "risk_output": {"is_safe": True, "circuit_breaker_active": False},
        }
    )
    result = await agent.process(ctx)
    assert result.output["decision"] == "SELL"


@pytest.mark.asyncio
async def test_circuit_breaker_overrides_to_hold():
    agent = ExecutorAgent()
    ctx = AgentContext(
        input_data={
            "quant_output": {"composite_score": 90},
            "risk_output": {
                "is_safe": True,
                "circuit_breaker_active": True,
                "confidence": 0.3,
            },
        }
    )
    result = await agent.process(ctx)
    assert result.output["decision"] == "HOLD"
    assert result.output["is_risk_overridden"] is True


@pytest.mark.asyncio
async def test_is_safe_false_overrides_to_hold():
    agent = ExecutorAgent()
    ctx = AgentContext(
        input_data={
            "quant_output": {"composite_score": 80},
            "risk_output": {"is_safe": False, "circuit_breaker_active": False},
        }
    )
    result = await agent.process(ctx)
    assert result.output["decision"] == "HOLD"
    assert result.output["is_risk_overridden"] is True


@pytest.mark.asyncio
async def test_journal_entry_appended_after_decision():
    journal = DecisionJournal()
    agent = ExecutorAgent(journal=journal)
    ctx = AgentContext(
        input_data={
            "token": "SOL/USDT",
            "quant_output": {"composite_score": 75},
            "risk_output": {"is_safe": True, "circuit_breaker_active": False},
            "research_output": {"signal": "bullish"},
        }
    )
    await agent.process(ctx)
    assert len(journal.entries) == 1
    entry = journal.entries[0]
    assert entry.token == "SOL/USDT"
    assert entry.decision == "BUY"


@pytest.mark.asyncio
async def test_output_contains_all_expected_keys():
    agent = ExecutorAgent()
    ctx = AgentContext(
        input_data={
            "quant_output": {"composite_score": 70},
            "risk_output": {"is_safe": True, "circuit_breaker_active": False},
            "current_price": 100.0,
        }
    )
    result = await agent.process(ctx)
    expected_keys = ["decision", "size_usd", "max_slippage", "stop_loss", "take_profit", "is_risk_overridden", "decision_rationale"]
    for key in expected_keys:
        assert key in result.output