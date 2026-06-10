"""Tests for Orchestrator module."""

from __future__ import annotations

import pytest

from kairos.core.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_orchestrator_creates_all_agents():
    orchestrator = Orchestrator()
    assert orchestrator.research_agent is not None
    assert orchestrator.quant_agent is not None
    assert orchestrator.risk_agent is not None
    assert orchestrator.executor_agent is not None
    assert orchestrator.sentiment_agent is not None
    assert orchestrator.journal is not None


@pytest.mark.asyncio
async def test_run_returns_dict_with_expected_keys():
    orchestrator = Orchestrator()
    result = await orchestrator.run(token="SOL/USDT", mode="demo", seed=42)
    assert isinstance(result, dict)
    assert "decision" in result
    assert "trace" in result
    assert "journal_entries" in result


@pytest.mark.asyncio
async def test_decision_contains_expected_keys():
    orchestrator = Orchestrator()
    result = await orchestrator.run(token="SOL/USDT", mode="demo", seed=42)
    decision = result["decision"]
    expected_keys = ["decision", "size_usd", "max_slippage", "stop_loss", "take_profit", "is_risk_overridden", "decision_rationale"]
    for key in expected_keys:
        assert key in decision, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_trace_has_five_entries():
    orchestrator = Orchestrator()
    result = await orchestrator.run(token="SOL/USDT", mode="demo", seed=42)
    trace = result["trace"]
    assert len(trace) == 5
    assert trace[0]["agent_name"] == "research"
    assert trace[1]["agent_name"] == "quant"
    assert trace[2]["agent_name"] == "risk"
    assert trace[3]["agent_name"] == "sentiment"
    assert trace[4]["agent_name"] == "executor"


@pytest.mark.asyncio
async def test_journal_entries_incremented_after_run():
    orchestrator = Orchestrator()
    initial_entries = len(orchestrator.journal.get_all())
    result = await orchestrator.run(token="SOL/USDT", mode="demo", seed=42)
    assert result["journal_entries"] > initial_entries
    assert result["journal_entries"] > 0
