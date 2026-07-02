"""Orchestrator module for Kairos - pipeline coordinator that runs all agents in sequence."""

from __future__ import annotations

from kairos.agents.base import AgentContext
from kairos.core.journal import DecisionJournal


class Orchestrator:
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._research_agent = None
        self._quant_agent = None
        self._risk_agent = None
        self._executor_agent = None
        self._sentiment_agent = None
        self.journal = DecisionJournal()

    @property
    def research_agent(self):
        if self._research_agent is None:
            from kairos.agents.research import ResearchAgent

            self._research_agent = ResearchAgent(self.config)
        return self._research_agent

    @property
    def quant_agent(self):
        if self._quant_agent is None:
            from kairos.agents.quant import QuantAgent

            self._quant_agent = QuantAgent(self.config)
        return self._quant_agent

    @property
    def risk_agent(self):
        if self._risk_agent is None:
            from kairos.agents.risk import RiskAgent

            self._risk_agent = RiskAgent(self.config)
        return self._risk_agent

    @property
    def executor_agent(self):
        if self._executor_agent is None:
            from kairos.agents.executor import ExecutorAgent

            self._executor_agent = ExecutorAgent(self.config, journal=self.journal)
        return self._executor_agent

    @property
    def sentiment_agent(self):
        if self._sentiment_agent is None:
            from kairos.agents.sentiment import SentimentAgent

            self._sentiment_agent = SentimentAgent(self.config)
        return self._sentiment_agent

    async def run(
        self,
        token: str = "SOL/USDT",
        mode: str = "demo",
        seed: int = 42,
    ) -> dict:
        research_result = await self.research_agent.process(
            AgentContext(input_data={"token": token, "mode": mode, "seed": seed})
        )

        ohlcv = research_result.output.get("ohlcv")
        if isinstance(ohlcv, dict):
            import pandas as pd

            ohlcv = pd.DataFrame.from_dict(ohlcv, orient="index")
        quant_result = await self.quant_agent.process(
            AgentContext(input_data={"ohlcv": ohlcv, "token": token, "mode": mode})
        )

        ap = self.config.get("agent_params", {}).get("default", {})
        risk_context = AgentContext(
            input_data={
                "returns": None,
                "portfolio_value": ap.get("portfolio_value", 10000),
                "win_rate": ap.get("win_rate", 0.5),
                "avg_win": ap.get("avg_win", 0.05),
                "avg_loss": ap.get("avg_loss", 0.03),
                "token": token,
                "mode": mode,
            }
        )
        risk_result = await self.risk_agent.process(risk_context)

        sentiment_result = await self.sentiment_agent.process(AgentContext(input_data={"token": token, "mode": mode}))

        executor_context = AgentContext(
            input_data={
                "quant_output": quant_result.output,
                "risk_output": risk_result.output,
                "research_output": research_result.output,
                "sentiment_output": sentiment_result.output,
                "token": token,
                "mode": mode,
            }
        )
        executor_result = await self.executor_agent.process(executor_context)

        trace = [
            _agent_result_to_dict(research_result),
            _agent_result_to_dict(quant_result),
            _agent_result_to_dict(risk_result),
            _agent_result_to_dict(sentiment_result),
            _agent_result_to_dict(executor_result),
        ]

        return {
            "decision": executor_result.output,
            "trace": trace,
            "journal_entries": len(self.journal.get_all()),
        }


def _agent_result_to_dict(result) -> dict:
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result.__dict__
