<div align="center">

# Kairos

**AI Trading Agents — Fully Transparent & Verifiable**

*The first open-source framework for building transparent, backtestable, statistically-validated AI trading agents.*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://www.python.org/downloads/)
[![CI](https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?branch=master&style=flat-square)](https://github.com/Electricitysheep/kairos/actions)
[![License: MIT](https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Electricitysheep/kairos?style=flat-square)](https://github.com/Electricitysheep/kairos/stargazers)

[English](README.md) · [中文](README.zh.md)

</div>

---

## Why Kairos?

Most AI trading tools are **black boxes** — they hand you a signal with no way to check the logic. Kairos takes the opposite bet: **every decision is deterministic, transparent, and verifiable.**

- 🔍 **Fully auditable decisions** — each of the 5 agents is rule-based (no LLM, no hidden model) and records the exact rationale behind every call.
- 📈 **Walk-Forward backtesting** — academic-grade rolling-window validation, not overfit curve-fitting.
- 🧪 **Bootstrap statistics** — p-values and confidence intervals so you know if an edge is real or noise.

> *Kairos* (καιρός) — Ancient Greek for "the opportune moment": the instant between signal and execution where opportunity lives.

## Quickstart

```bash
pip install git+https://github.com/Electricitysheep/kairos.git
kairos demo          # zero-config demo, no API keys needed
kairos analyze AAPL  # live stock / crypto analysis
```

That's it — `kairos demo` runs the full 5-agent pipeline on sample data with no setup.

## Features

- **5 specialized agents** — Research → Quant → Risk → Sentiment → Executor, run as a coordinated pipeline
- **Walk-Forward Backtesting** — rolling-window out-of-sample validation
- **Bootstrap Statistics** — p-values and confidence intervals on strategy returns
- **Strategy Plugin System** — write custom strategies as plain Python classes
- **6 Built-in Strategies** — momentum, mean_reversion, conservative, rsi, bb, ensemble
- **Paper + Live Trading** — via Alpaca (free paper trading)
- **HTML Reports** — one-click shareable research report
- **6 Data Sources** — Yahoo Finance, FRED, CoinGecko, DexScreener, Birdeye, Mock

## CLI Commands

| Command | Description |
|---------|-------------|
| `kairos demo` | Zero-friction demo (no API keys) |
| `kairos analyze AAPL` | Real-time stock / crypto analysis |
| `kairos leaderboard AAPL` | Rank all 6 strategies by performance |
| `kairos backtest --token AAPL` | Walk-Forward backtesting |
| `kairos compare AAPL MSFT` | Compare tickers side by side |
| `kairos report AAPL` | Generate an HTML research report |
| `kairos paper AAPL --qty 10` | Paper trading via Alpaca |
| `kairos live AAPL --qty 10` | Live trading via Alpaca |
| `kairos dashboard` | Launch the interactive dashboard |

## Architecture

Kairos runs five specialized agents as a sequential pipeline, coordinated by an `Orchestrator`. Each agent emits a structured result, and the full trace is persisted to a decision journal.

```
Research ─▶ Quant ─▶ Risk ─▶ Sentiment ─▶ Executor
   │          │        │          │           │
   └──────────┴────────┴──────────┴───────────┘
                       ▼
             Decision Journal (full decision trace)
```

```
src/kairos/
├── agents/        # Research, Quant, Risk, Sentiment, Executor
├── backtesting/   # Walk-Forward engine, metrics, optimizer, portfolio
├── strategies/    # Base class, built-ins, plugin registry
├── data/          # Providers (Yahoo, FRED, CoinGecko, DexScreener, Birdeye)
├── statistics/    # Bootstrap significance testing
├── brokers/       # Alpaca paper + live
├── core/          # Orchestrator, config, decision journal
├── reports/       # HTML report generation
├── dashboard/     # Streamlit dashboard
└── cli/           # Typer CLI
```

## Custom Strategy Example

```python
from kairos.strategies.base import Strategy, StrategyContext, Signal

class MyStrategy(Strategy):
    def compute_signal(self, ctx: StrategyContext) -> Signal:
        price = ctx.latest()
        if price > self.config.get("threshold", 100):
            return Signal.buy(confidence=0.7, reason=f"Price {price:.2f} above threshold")
        return Signal.hold()
```

Register it, and it shows up in `kairos leaderboard` and `kairos backtest` automatically. See [`examples/custom_strategy.py`](examples/custom_strategy.py) and [`notebooks/01_kairos_quickstart.ipynb`](notebooks/01_kairos_quickstart.ipynb) for full walkthroughs.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Good first steps: add a strategy, add a data provider, or improve the docs.

## Disclaimer

Kairos is a research and educational tool. It is **not financial advice**. Trading involves risk of loss. Use paper trading first, and never trade with money you can't afford to lose.

## License

[MIT](LICENSE) © Zhou Yuchen
