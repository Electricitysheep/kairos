"""QuantAgent - Technical analysis and quantitative signals."""

from __future__ import annotations

from kairos.agents.base import AgentBase, AgentContext, AgentResult
from kairos.data.mock import MockDataProvider
from kairos.indicators.ta import TAAnalyzer


class QuantAgent(AgentBase):
    """Agent that computes technical analysis indicators and produces quantitative signals."""

    @property
    def name(self) -> str:
        return "quant"

    async def process(self, context: AgentContext) -> AgentResult:
        """Process market data and compute technical indicators.

        Args:
            context: AgentContext with optional 'ohlcv' in input_data

        Returns:
            AgentResult with technical analysis output
        """
        # Get OHLCV data from context or generate mock data
        if "ohlcv" in context.input_data and context.input_data["ohlcv"] is not None:
            df = context.input_data["ohlcv"]
        else:
            # Generate mock data for demonstration
            df = MockDataProvider.generate_price_data(days=30, seed=42)

        # Compute all technical indicators
        indicators = TAAnalyzer.compute_all(df)

        # Extract values
        rsi_14 = indicators["rsi_14"]
        macd = indicators["macd"]
        bb = indicators["bb"]
        ema_9 = indicators["ema_9"]
        ema_21 = indicators["ema_21"]
        ema_50 = indicators["ema_50"]
        adx_14 = indicators["adx_14"]
        atr_14 = indicators["atr_14"]
        composite_score = indicators["composite_score"]

        # Determine signal based on composite score
        if composite_score > 65:
            signal = "bullish"
        elif composite_score < 35:
            signal = "bearish"
        else:
            signal = "neutral"

        # Determine signal strength
        score_deviation = abs(composite_score - 50)
        if score_deviation > 25:
            signal_strength = "strong"
        elif score_deviation > 15:
            signal_strength = "moderate"
        else:
            signal_strength = "weak"

        # Build output dict
        output = {
            "rsi_14": rsi_14,
            "macd": macd,
            "bb": bb,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "ema_50": ema_50,
            "adx_14": adx_14,
            "atr_14": atr_14,
            "composite_score": composite_score,
            "signal": signal,
            "signal_strength": signal_strength,
        }

        # Build reasoning string
        reasoning_parts = []
        reasoning_parts.append(f"RSI at {rsi_14:.1f}")
        if macd["is_bullish_cross"]:
            reasoning_parts.append("MACD bullish cross")
        reasoning_parts.append(f"composite_score {composite_score:.0f}")
        reasoning = ", ".join(reasoning_parts)

        # Confidence is the normalized composite score (0-1)
        confidence = max(0.0, min(1.0, composite_score / 100.0))

        return AgentResult(
            agent_name=self.name,
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            metadata={"agent": "QuantAgent"},
        )