"""Risk agent for calculating risk metrics."""

from __future__ import annotations

import numpy as np

from kairos.agents.base import AgentBase, AgentContext, AgentResult


class RiskAgent(AgentBase):
    """Agent that calculates risk metrics including VaR, CVaR, and Kelly Criterion."""

    @property
    def name(self) -> str:
        return "risk"

    async def process(self, context: AgentContext) -> AgentResult:
        """Process the context and calculate risk metrics."""
        input_data = context.input_data
        config = context.config

        # Extract inputs
        returns = input_data.get("returns")
        portfolio_value = input_data.get("portfolio_value", 10000.0)
        win_rate = input_data.get("win_rate", 0.5)
        avg_win = input_data.get("avg_win", 0.05)
        avg_loss = input_data.get("avg_loss", 0.03)
        max_position_pct = config.get("max_position_pct", 0.1)
        circuit_breaker_active = input_data.get("circuit_breaker", False)

        # 1. Value at Risk (VaR)
        if returns is not None and len(returns) > 0:
            var_95 = float(np.percentile(returns, 5))
            var_99 = float(np.percentile(returns, 1))
        else:
            var_95 = -0.03
            var_99 = -0.05

        # 2. Expected Shortfall (CVaR)
        if returns is not None and len(returns) > 0:
            tail = [r for r in returns if r <= var_95]
            cvar_95 = float(np.mean(tail)) if len(tail) > 0 else var_95
        else:
            cvar_95 = -0.05

        # 3. Kelly Criterion
        if avg_loss != 0:
            win_ratio = avg_win / abs(avg_loss)
            p = win_rate
            q = 1 - p
            kelly_fraction = (p * win_ratio - q) / win_ratio
        else:
            kelly_fraction = 0.0

        # Clamp Kelly to [0, 0.5]
        kelly_fraction = max(0.0, min(0.5, kelly_fraction))

        # 4. Position Sizing
        max_position = portfolio_value * max_position_pct
        kelly_position = portfolio_value * kelly_fraction

        # 5. Safety check
        is_safe = var_95 > -0.05 and not circuit_breaker_active

        output = {
            "var_95": var_95,
            "var_99": var_99,
            "cvar_95": cvar_95,
            "kelly_fraction": kelly_fraction,
            "max_position": max_position,
            "kelly_position": kelly_position,
            "portfolio_value": portfolio_value,
            "circuit_breaker_active": circuit_breaker_active,
            "is_safe": is_safe,
        }

        return AgentResult(
            agent_name=self.name,
            output=output,
            confidence=1.0,
            reasoning="Risk metrics calculated from portfolio and return data.",
        )
