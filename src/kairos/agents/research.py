"""Research agent for market data collection."""

from __future__ import annotations

from kairos.agents.base import AgentBase, AgentContext, AgentResult
from kairos.data.mock import MockDataProvider


class ResearchAgent(AgentBase):
    """Agent that collects market research data for trading pairs.

    Supports two modes:
    - demo: uses MockDataProvider (no API keys needed)
    - live: uses real DataProviders (requires API keys/config)
    """

    def __init__(self, config=None, data_provider=None):
        super().__init__(config)
        self._data_provider = data_provider

    @property
    def name(self) -> str:
        return "research"

    async def process(self, context: AgentContext) -> AgentResult:
        mode = context.input_data.get("mode", "demo")
        token = context.input_data.get("token", "SOL/USDT")
        seed = context.input_data.get("seed", 42)

        if mode == "demo":
            return await self._demo_mode(token, seed)
        elif mode == "live" and self._data_provider is not None:
            return await self._live_mode(token)
        else:
            return AgentResult(
                agent_name=self.name,
                output={
                    "error": "Live mode requires a DataProvider. "
                    "Pass data_provider to ResearchAgent or use mode='demo'."
                },
                confidence=0.0,
                reasoning="Live mode attempted without DataProvider.",
                metadata={"mode": mode, "token": token},
            )

    async def _demo_mode(self, token: str, seed: int) -> AgentResult:
        research_packet = MockDataProvider.generate_research_packet(token, seed)
        ohlcv_df = MockDataProvider.generate_price_data(days=30, seed=seed)

        output = {
            "token": token,
            "price_data": research_packet["price_summary"],
            "volume_data": {"volume_24h": research_packet["volume_24h"]},
            "ohlcv": ohlcv_df.to_dict(orient="index"),
            "technical_summary": research_packet["technical_summary"],
            "data_quality": research_packet["data_quality"],
        }

        return AgentResult(
            agent_name=self.name,
            output=output,
            confidence=0.8,
            reasoning=f"Collected market research data for {token} in demo mode.",
            metadata={"mode": "demo", "seed": seed},
        )

    async def _live_mode(self, token: str) -> AgentResult:
        try:
            price_df = await self._data_provider.fetch_price_data(token, days=30)
            market_data = await self._data_provider.fetch_market_data(token)

            output = {
                "token": token,
                "price_data": {
                    "current": market_data.get("price", 0),
                    "volume_24h": market_data.get("volume_24h", 0),
                    "change_24h": market_data.get("price_change_24h", 0),
                },
                "volume_data": {"volume_24h": market_data.get("volume_24h", 0)},
                "ohlcv": price_df.to_dict(orient="index") if price_df is not None else {},
                "technical_summary": f"Live data collected for {token}.",
                "data_quality": "good",
            }

            return AgentResult(
                agent_name=self.name,
                output=output,
                confidence=0.9,
                reasoning=f"Collected live market data for {token}.",
                metadata={"mode": "live", "token": token},
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                output={"error": f"Live data fetch failed: {e}"},
                confidence=0.0,
                reasoning=f"Failed to fetch live data for {token}: {e}",
                metadata={"mode": "live", "token": token},
            )
