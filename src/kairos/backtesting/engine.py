"""Walk-forward backtesting engine for Kairos agents."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable

import pandas as pd

from kairos.backtesting.metrics import PerformanceMetrics
from kairos.backtesting.portfolio import SimulatedPortfolio
from kairos.backtesting.splitter import WalkForwardSplitter, WindowIndices
from kairos.indicators.ta import TAAnalyzer

if TYPE_CHECKING:
    from kairos.agents.executor import ExecutorAgent
    from kairos.agents.quant import QuantAgent
    from kairos.agents.risk import RiskAgent


class WalkForwardEngine:
    """Walk-forward backtesting engine with pre-computed indicators."""

    def __init__(
        self,
        data: pd.DataFrame,
        agent_config: dict | None = None,
        train_size: int = 90,
        test_size: int = 30,
        step_size: int = 30,
        embargo: int = 5,
        mode: str = "rolling",
        initial_cash: float = 10000.0,
        quant_agent: QuantAgent | None = None,
        risk_agent: RiskAgent | None = None,
        executor_agent: ExecutorAgent | None = None,
        max_windows: int | None = None,
    ):
        required_cols = {"open", "high", "low", "close", "volume"}
        if not required_cols.issubset(data.columns):
            raise ValueError(f"Data must have columns: {required_cols}")
        if len(data) < train_size + test_size + embargo:
            raise ValueError("Insufficient data for even one window")

        self.data = data
        self.agent_config = agent_config or {}
        self.train_size = train_size
        self.test_size = test_size
        self.step_size = step_size
        self.embargo = embargo
        self.mode = mode
        self.initial_cash = initial_cash
        self._quant_agent = quant_agent
        self._risk_agent = risk_agent
        self._executor_agent = executor_agent
        self.max_windows = max_windows
        self._precomputed = None

    @property
    def quant_agent(self):
        if self._quant_agent is None and self._has_any_agent():
            from kairos.agents.quant import QuantAgent

            self._quant_agent = QuantAgent(self.agent_config)
        return self._quant_agent

    @property
    def risk_agent(self):
        if self._risk_agent is None and self._has_any_agent():
            from kairos.agents.risk import RiskAgent

            self._risk_agent = RiskAgent(self.agent_config)
        return self._risk_agent

    @property
    def executor_agent(self):
        if self._executor_agent is None and self._has_any_agent():
            from kairos.agents.executor import ExecutorAgent

            self._executor_agent = ExecutorAgent(self.agent_config)
        return self._executor_agent

    def _has_any_agent(self) -> bool:
        return any([self._quant_agent, self._risk_agent, self._executor_agent])

    def _precompute_indicators(self) -> pd.DataFrame:
        """Compute all TA indicators once across the full dataset.

        Returns a DataFrame with indicator columns aligned to the original data index.
        This avoids recomputing indicators for every bar in every window (100x+ faster).
        """
        result = self.data[["close"]].copy()
        result["rsi_14"] = TAAnalyzer.compute_rsi(self.data, period=14)
        result["ema_9"] = TAAnalyzer.compute_ema(self.data, period=9)
        result["ema_21"] = TAAnalyzer.compute_ema(self.data, period=21)
        macd = TAAnalyzer.compute_macd_series(self.data)
        result["macd_histogram"] = macd["histogram"]
        result["macd_bullish"] = macd["is_bullish_cross"].astype(int)
        bb = TAAnalyzer.compute_bollinger_series(self.data)
        result["bb_percent_b"] = bb["percent_b"]
        result["bb_upper"] = bb["upper"]
        result["bb_mid"] = bb["mid"]
        result["bb_lower"] = bb["lower"]
        return result

    def _composite_from_precomputed(self, row: pd.Series) -> float:
        """Compute composite score from a pre-computed indicator row."""
        rsi = row.get("rsi_14", 50)
        score = rsi * 0.4
        score += 20 if row.get("macd_bullish", 0) else 0
        pct_b = row.get("bb_percent_b", 0.5)
        if pd.isna(pct_b):
            pct_b = 0.5
        score += pct_b * 20
        close = row.get("close", 0)
        ema21 = row.get("ema_21", 0)
        score += 20 if (not pd.isna(close) and not pd.isna(ema21) and close > ema21) else 0
        return max(0.0, min(100.0, score))

    def run(
        self,
        strategy_config: dict | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict:
        """Run the walk-forward backtest with optional progress reporting.

        Args:
            strategy_config: Overrides agent_config for this run.
            progress_callback: Called as progress_callback(current, total) after each window.
        """
        config = {**self.agent_config, **(strategy_config or {})}
        splitter = WalkForwardSplitter(
            n_samples=len(self.data),
            train_size=self.train_size,
            test_size=self.test_size,
            step_size=self.step_size,
            embargo=self.embargo,
            mode=self.mode,
        )
        windows = splitter.split()
        if self.max_windows is not None:
            windows = windows[: self.max_windows]
        all_returns: list[float] = []
        self._precomputed = self._precompute_indicators()

        for i, window in enumerate(windows):
            window_returns = self._run_window(window, config)
            all_returns.extend(window_returns)
            if progress_callback:
                progress_callback(i + 1, len(windows))

        metrics = PerformanceMetrics(all_returns)

        # Benchmark: buy-and-hold for the entire period (vectorized)
        close = self.data["close"].astype(float)
        prev_close = close.shift(1)
        bench = (close - prev_close) / prev_close
        benchmark_returns = bench[prev_close > 0].dropna().tolist()
        benchmark_metrics = PerformanceMetrics(benchmark_returns)

        return {
            "aggregate": metrics.compute_all(),
            "benchmark": benchmark_metrics.compute_all(),
            "all_returns": all_returns,
            "n_windows": len(windows),
            "strategy_config": config,
        }

    def _run_window(self, window: WindowIndices, config: dict) -> list[float]:
        portfolio = SimulatedPortfolio(initial_cash=self.initial_cash)
        window_returns: list[float] = []

        for idx, (_, row) in enumerate(self.data.iloc[window.test_start : window.test_end].iterrows()):
            abs_idx = window.test_start + idx
            current_data = self.data.iloc[: abs_idx + 1]

            if self._has_any_agent() and self._quant_agent and self._executor_agent:
                decision = self._get_decision_from_agents(current_data, float(row["close"]))
            else:
                decision = self._get_decision_classic(abs_idx, config)

            portfolio.update_price(float(row["close"]))
            if decision != "HOLD":
                pos_size = config.get("position_size", 1000)
                portfolio.execute_trade(decision, float(row["close"]), value=pos_size)

            prev = portfolio.snapshots[-2].total_value if len(portfolio.snapshots) >= 2 else portfolio.initial_cash
            curr = portfolio.total_value
            if prev > 0:
                window_returns.append((curr - prev) / prev)

        return window_returns

    def _get_decision_classic(self, abs_idx: int, config: dict) -> str:
        """Use pre-computed indicator row + threshold logic."""
        if self._precomputed is None or abs_idx >= len(self._precomputed):
            return "HOLD"
        row = self._precomputed.iloc[abs_idx]
        composite = self._composite_from_precomputed(row)
        buy_threshold = config.get("buy_threshold", 60)
        sell_threshold = config.get("sell_threshold", 40)
        enable_sell = config.get("enable_sell", True)

        if composite > buy_threshold:
            return "BUY"
        elif composite < sell_threshold and enable_sell:
            return "SELL"
        return "HOLD"

    def _get_decision_from_agents(self, current_data: pd.DataFrame, price: float) -> str:
        from kairos.agents.base import AgentContext

        async def _decision():
            qctx = AgentContext(input_data={"ohlcv": current_data})
            qr = await self.quant_agent.process(qctx)
            from kairos.data.mock import MockDataProvider

            mock = MockDataProvider.generate_research_packet("backtest")
            rctx = AgentContext(
                input_data={
                    "returns": None,
                    "portfolio_value": self.initial_cash,
                    "win_rate": 0.5,
                    "avg_win": 0.05,
                    "avg_loss": 0.03,
                }
            )
            rr = await self.risk_agent.process(rctx) if self._risk_agent else None
            ectx = AgentContext(
                input_data={
                    "quant_output": qr.output,
                    "risk_output": rr.output if rr else {"is_safe": True, "circuit_breaker_active": False},
                    "research_output": mock,
                    "token": "BACKTEST",
                    "mode": "backtest",
                    "current_price": price,
                }
            )
            er = await self.executor_agent.process(ectx)
            return er.output.get("decision", "HOLD")

        return asyncio.run(_decision())
