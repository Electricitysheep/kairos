"""Tests for SentimentAgent."""

from __future__ import annotations

import pytest

from kairos.agents.sentiment import SentimentAgent, _score_headline
from kairos.agents.base import AgentContext


class TestSentimentScoring:
    def test_positive_headline(self):
        score, label = _score_headline("AAPL beats earnings estimates, stock surges")
        assert label == "bullish"
        assert score > 0

    def test_negative_headline(self):
        score, label = _score_headline("Markets crash amid recession fears")
        assert label == "bearish"
        assert score < 0

    def test_neutral_headline(self):
        score, label = _score_headline("AAPL trading flat in afternoon session")
        assert label == "neutral"

    def test_empty_headline(self):
        score, label = _score_headline("")
        assert label == "neutral"
        assert score == 0.0

    def test_mixed_sentiment(self):
        score, label = _score_headline("Strong growth but rising debt concerns")
        assert label in ("bullish", "bearish", "neutral")


class TestSentimentAgent:
    @pytest.mark.asyncio
    async def test_name_property(self):
        agent = SentimentAgent()
        assert agent.name == "sentiment"

    @pytest.mark.asyncio
    async def test_demo_mode_returns_sentiment(self):
        agent = SentimentAgent()
        result = await agent.process(AgentContext(input_data={"token": "AAPL", "mode": "demo"}))
        assert result.agent_name == "sentiment"
        assert "sentiment" in result.output
        assert "score" in result.output
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_demo_mode_deterministic(self):
        agent = SentimentAgent()
        r1 = await agent.process(AgentContext(input_data={"token": "AAPL", "mode": "demo"}))
        r2 = await agent.process(AgentContext(input_data={"token": "AAPL", "mode": "demo"}))
        assert r1.output["sentiment"] == r2.output["sentiment"]

    @pytest.mark.asyncio
    async def test_different_tokens_different_sentiment(self):
        agent = SentimentAgent()
        r1 = await agent.process(AgentContext(input_data={"token": "AAPL", "mode": "demo"}))
        r2 = await agent.process(AgentContext(input_data={"token": "MSFT", "mode": "demo"}))
        assert r1.output["token"] != r2.output["token"]
