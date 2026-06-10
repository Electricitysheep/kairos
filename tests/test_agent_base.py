"""Tests for agent base classes."""

from __future__ import annotations

import pytest

from kairos.agents.base import AgentBase, AgentContext, AgentResult


class ConcreteAgent(AgentBase):
    @property
    def name(self) -> str:
        return "concrete"

    async def process(self, context: AgentContext) -> AgentResult:
        return AgentResult(agent_name=self.name, output={"result": "processed"})


def test_agentbase_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AgentBase()


def test_subclass_must_implement_process():
    class IncompleteAgent(AgentBase):
        @property
        def name(self) -> str:
            return "incomplete"

    with pytest.raises(TypeError):
        IncompleteAgent()


def test_agent_context_creation():
    ctx = AgentContext(
        input_data={"key": "value"},
        config={"setting": 42},
        metadata={"meta": "data"}
    )
    assert ctx.input_data == {"key": "value"}
    assert ctx.config == {"setting": 42}
    assert ctx.metadata == {"meta": "data"}


def test_agent_context_defaults():
    ctx = AgentContext()
    assert ctx.input_data == {}
    assert ctx.config == {}
    assert ctx.metadata == {}


def test_agent_result_creation():
    result = AgentResult(
        agent_name="test",
        output={"output": "data"},
        confidence=0.95,
        reasoning="makes sense"
    )
    assert result.agent_name == "test"
    assert result.output == {"output": "data"}
    assert result.confidence == 0.95
    assert result.reasoning == "makes sense"


def test_agent_result_defaults():
    result = AgentResult(agent_name="test")
    assert result.output == {}
    assert result.confidence == 0.0
    assert result.reasoning == ""
    assert result.metadata == {}


def test_agent_name_property():
    agent = ConcreteAgent(config={"option": True})
    assert agent.name == "concrete"


def test_timestamp_auto_generated():
    result = AgentResult(agent_name="test")
    assert result.timestamp != ""
    assert "T" in result.timestamp
    assert "+" in result.timestamp or "Z" in result.timestamp


def test_timestamp_custom_value():
    custom_ts = "2024-01-01T00:00:00+00:00"
    result = AgentResult(agent_name="test", timestamp=custom_ts)
    assert result.timestamp == custom_ts


@pytest.mark.asyncio
async def test_process_returns_agent_result():
    ctx = AgentContext(input_data={"data": "test"})
    agent = ConcreteAgent()
    result = await agent.process(ctx)
    assert isinstance(result, AgentResult)
    assert result.agent_name == "concrete"
    assert result.output == {"result": "processed"}