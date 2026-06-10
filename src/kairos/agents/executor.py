"""ExecutorAgent for Kairos - final trading decision aggregation."""

from __future__ import annotations

from datetime import datetime, timezone

from kairos.agents.base import AgentBase, AgentContext, AgentResult
from kairos.core.journal import DecisionJournal, JournalEntry


class ExecutorAgent(AgentBase):
    """Executor agent that aggregates outputs from Research, Quant, and Risk agents to make final trading decisions."""

    def __init__(self, config=None, journal: DecisionJournal | None = None):
        """Initialize the ExecutorAgent with optional config and journal."""
        super().__init__(config)
        self.journal = journal or DecisionJournal()

    @property
    def name(self) -> str:
        return "executor"

    async def process(self, context: AgentContext) -> AgentResult:
        """Process the context and make a final trading decision."""
        input_data = context.input_data

        # Extract inputs
        quant_output = input_data.get("quant_output", {})
        risk_output = input_data.get("risk_output", {})
        research_output = input_data.get("research_output", {})
        token = input_data.get("token", "SOL/USDT")
        mode = input_data.get("mode", "demo")

        # Get thresholds from config
        buy_threshold = self._config.get("buy_threshold", 60)
        sell_threshold = self._config.get("sell_threshold", 40)

        # Decision variables
        decision = "HOLD"
        confidence = 0.5
        is_risk_overridden = False
        decision_rationale = ""

        # Get current price if available
        current_price = input_data.get("current_price")

        # Decision Logic
        # Step 1: Check circuit breaker from risk_output
        if risk_output.get("circuit_breaker_active", False):
            decision = "HOLD"
            confidence = risk_output.get("confidence", 0.3)
            decision_rationale = "Circuit breaker active - holding position"
            is_risk_overridden = True

        # Step 2: Check is_safe from risk_output
        elif risk_output.get("is_safe", True) is False:
            decision = "HOLD"
            confidence = risk_output.get("confidence", 0.4)
            decision_rationale = "Risk assessment negative - holding position"
            is_risk_overridden = True

        # Step 3: Use composite_score for decision
        else:
            composite_score = quant_output.get("composite_score", 50)

            if composite_score > buy_threshold:
                decision = "BUY"
                confidence = min(1.0, composite_score / 100)
                decision_rationale = f"Composite score {composite_score:.1f} above buy threshold {buy_threshold}"
            elif composite_score < sell_threshold:
                # Check if sell is supported, else HOLD
                decision = "SELL" if self._config.get("enable_sell", True) else "HOLD"
                confidence = min(1.0, (100 - composite_score) / 100)
                if decision == "SELL":
                    decision_rationale = f"Composite score {composite_score:.1f} below sell threshold {sell_threshold}"
                else:
                    decision_rationale = f"Composite score {composite_score:.1f} below sell threshold {sell_threshold} - holding (sell disabled)"
            else:
                decision = "HOLD"
                confidence = 0.5
                decision_rationale = f"Composite score {composite_score:.1f} within neutral range [{sell_threshold}, {buy_threshold}]"

        # Position Sizing
        # Use kelly_position if available, else max_position
        kelly_position = risk_output.get("kelly_position")
        max_position = risk_output.get("max_position", 1000)

        if kelly_position is not None:
            size_usd = min(kelly_position, max_position)
        else:
            size_usd = max_position

        # Slippage settings
        max_slippage = self._config.get("max_slippage", 0.003)

        # Stop loss and take profit
        stop_loss = None
        take_profit = None
        if current_price is not None:
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.15

        # Build output dict
        output = {
            "decision": decision,
            "size_usd": size_usd,
            "max_slippage": max_slippage,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "is_risk_overridden": is_risk_overridden,
            "decision_rationale": decision_rationale,
        }

        # Create journal entry
        entry = JournalEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            token=token,
            decision=decision,
            confidence=confidence,
            reasoning_summary=decision_rationale,
            data_sources=["research", "quant", "risk"],
            research_agent=research_output if research_output else {},
            quant_agent=quant_output if quant_output else {},
            risk_agent=risk_output if risk_output else {},
            final_action=output,
        )

        self.journal.append(entry)

        return AgentResult(
            agent_name=self.name,
            output=output,
            confidence=confidence,
            reasoning=decision_rationale,
        )