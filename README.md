<div align="center">

# Kairos

**AI Trading Agents — Fully Transparent & Verifiable**

*The first open-source framework for building transparent, backtestable, statistically-validated AI trading agents.*

[![PyPI](https://img.shields.io/pypi/v/kairos-agent?style=flat-square)](https://pypi.org/project/kairos-agent/)
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

## Point-in-time correctness

The engine's core constraint: **a decision attributed to bar _i_ may use only information available at bar _i_.** Two guards enforce it:

- **Prefix invariance** — indicators computed over the full series must be identical, on the overlap, to indicators computed over any prefix of it. If appending future bars changes a past value, that value depended on the future. ([`tests/test_engine_precompute.py`](tests/test_engine_precompute.py))
- **Per-window parameter selection** — grid search runs on each window's **train** slice only; the winner is applied out-of-sample to the test slice, so parameters are never chosen on test data. ([`832ea84`](https://github.com/Electricitysheep/kairos/commit/832ea84))

These guards exist because I shipped a look-ahead bias and had to remove it ([`13d02dd`](https://github.com/Electricitysheep/kairos/commit/13d02dd)). `compute_macd()` and `compute_bollinger()` return scalars describing the **latest** bar; assigning them to DataFrame columns broadcast one future-derived value across every row, contaminating 40 of the 100 points in the composite score.

The instructive part: **it made results worse, not better.** On SPY (2020-01-02 – 2024-12-30, 1,257 daily bars) the leaked constants collapsed the signal so completely that the strategy generated one buy in the entire sample, never opened a position, and reported a Sharpe of exactly `0.0000`; after the fix, `0.9576`. Leakage is contamination, not inflation — its sign depends on the accidental content of the leaked value. That is why "performance looks too good" is an unreliable detector, and structural invariants are not.

> Measured on Python 3.14.2 / pandas 3.0.3, windows train=90, embargo=5, test=30, rolling. No transaction costs are modelled — see [Limitations](#limitations).

## Features

- **5 specialized agents** — Research → Quant → Risk → Sentiment → Executor, run as a coordinated pipeline
- **Walk-Forward Backtesting** — rolling-window out-of-sample validation with per-window parameter selection (grid search on each train slice, applied out-of-sample to the test slice)
- **Bootstrap Statistics** — p-values and confidence intervals on strategy returns
- **Strategy Plugin System** — write custom strategies as plain Python classes
- **6 Built-in Strategies** — momentum, mean_reversion, conservative, rsi, bb, ensemble
- **Paper + Live Trading** — via Alpaca (free paper trading)
- **HTML Reports** — one-click shareable research report
- **6 Data Sources** — Yahoo Finance, FRED, CoinGecko, DexScreener, Birdeye, Mock

### Walk-Forward Optimization

Parameters are selected on each window's **train** slice only, then applied
out-of-sample to its **test** slice — no test data leaks into selection:

```python
from kairos.backtesting.optimizer import StrategyOptimizer

optimizer = StrategyOptimizer(data, train_size=90, test_size=30)
result = optimizer.optimize_walk_forward({
    "buy_threshold": [55, 60, 70],
    "sell_threshold": [30, 40, 45],
})
print(result["aggregate"]["sharpe_ratio"])   # pooled out-of-sample Sharpe
print(result["window_params"])               # params chosen per window
```

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

## Run with Docker

```bash
docker build -t kairos .
docker run -p 8501:8501 kairos       # dashboard at http://localhost:8501
docker run kairos analyze AAPL       # or run any CLI command
```

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

## Limitations

Stated plainly, because a backtester that hides these is worse than useless:

- **No transaction costs** — commission, spread, and slippage are not modelled; trades use a fixed notional at the close price.
- **No execution lag** — signal and fill happen on the same bar at the same price, which a live system could not achieve.
- **Survivorship bias** — any tickers used in examples were selected with hindsight about which names survived.
- **Single-instrument accounting** — one position at a time; no cross-sectional sizing or portfolio-level risk control.
- **Price data only** — no fundamentals, so publication-date alignment of financial statements is out of scope here.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Good first steps: add a strategy, add a data provider, or improve the docs.

## Disclaimer

Kairos is a research and educational tool. It is **not financial advice**. Trading involves risk of loss. Use paper trading first, and never trade with money you can't afford to lose.

## License

[MIT](LICENSE) © Zhou Yuchen
