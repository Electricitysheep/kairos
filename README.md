# Kairos — AI Trading Agents, Fully Transparent & Verifiable

<p align="center">
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python"></a>
  <a href="https://github.com/Electricitysheep/kairos/actions"><img src="https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?style=flat-square" alt="CI"></a>
  <a href="https://github.com/Electricitysheep/kairos/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square" alt="License"></a>
  <a href="https://pypi.org/project/kairos-agent/"><img src="https://img.shields.io/pypi/v/kairos-agent?style=flat-square" alt="PyPI"></a>
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/github/stars/Electricitysheep/kairos?style=flat-square" alt="Stars"></a>
</p>

<p align="center">
  <b>AI Trading Agents, Fully Transparent &amp; Verifiable.</b>
  <br>
  <i>Research-grade agents for stocks, ETFs, and crypto — with full decision transparency.</i>
</p>

```text
┌─ Kairos Analyze — AAPL (stock) ──────────────────────────────────┐
│ ┌─────────── Decision ───────────┐  ┌────── Indicators ──────┐  │
│ │ BUY  (confidence: 50%)          │  │ Composite Score  67/100│  │
│ │ Composite score 67 above 65     │  │ RSI(14)          73.3  │  │
│ └─────────────────────────────────┘  │ Signal          BULLISH│  │
│ ┌────── AAPL Price Trend ────────┐   │ ADX              44.8  │  │
│ │ $314.23  +26.92% over 90 bars   │   └──────────────────────┘  │
│ │ ▁▂▃▅▆▇▇▆▅▄▃▂▁ (trend sparkline) │                              │
│ └─────────────────────────────────┘                              │
│ Research → Quant → Risk → Executor — every decision traceable    │
└──────────────────────────────────────────────────────────────────┘
```

**Not another black-box signal. Every decision comes with a complete, auditable reasoning trace.**

- **Transparent** — Watch your agent think in real-time via the Dashboard
- **Backtestable** — Walk-forward validation with statistical significance tests
- **Research-grade** — Bootstrap p-values, Sharpe ratios, drawdown analysis
- **Modular** — Extensible 4-agent architecture (Research, Quant, Risk, Executor)

---

## Quick Start

```bash
# 1. Install from GitHub (PyPI release coming soon)
pip install git+https://github.com/Electricitysheep/kairos.git

# 2. Run a full agent analysis (real data, no API keys)
kairos analyze AAPL

# 3. Run a walk-forward backtest
kairos backtest --token AAPL --days 730

# 4. Launch the interactive Dashboard
kairos dashboard
```

---

## Why Kairos?

| Feature | Other AI Agents | **Kairos** |
|---------|----------------|------------|
| See agent's reasoning | ❌ Black box | ✅ Full reasoning trace |
| Backtest strategies | ❌ Can't test | ✅ Walk-forward validation |
| Statistical significance | ❌ "Trust me" | ✅ Bootstrap p-value |
| Interactive dashboard | ❌ CLI only | ✅ Streamlit UI |
| Pre-built strategies | ❌ None | ✅ 3 built-in strategies |
| Real market data | ❌ Mock only | ✅ **5 sources** (stocks, crypto, ETFs) |
| Benchmark comparison | ❌ None | ✅ Buy-and-hold benchmark |
| Pythonic API | ❌ TypeScript | ✅ Python 3.10+ |
| Modular agents | ❌ Monolithic | ✅ 4 specialized agents |

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `kairos analyze AAPL` | **Analyze any stock/crypto** with the full 4-agent pipeline |
| `kairos backtest` | Run walk-forward backtest with statistical validation |
| `kairos dashboard` | Launch interactive Streamlit Dashboard |
| `kairos demo` | Run full demo with mock data (no API keys needed) |
| `kairos version` | Show version |

---

## Features

### 🧠 Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────┐
│  Orchestrator                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │ Research │→ │  Quant   │→ │  Risk    │→ │Exec │ │
│  │  Agent   │  │  Agent   │  │  Agent   │  │utor │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────┘ │
│       │              │             │          │      │
│  Market Data    TA Indicators  VaR/Kelly   Decision │
└─────────────────────────────────────────────────────┘
```

### 📊 Real-Time Dashboard
Monitor agent reasoning, technical indicators, risk metrics, and decision history in an interactive Streamlit dashboard.

### 📈 Walk-Forward Backtesting
Statistically rigorous backtesting with rolling windows, embargo gaps, and comprehensive performance metrics.

### 🔬 Bootstrap Significance Tests
Don't trust your backtest results? Kairos computes p-values and confidence intervals to tell you if your strategy is statistically significant.

### 🔗 Multiple Data Sources (Stocks, Crypto, ETFs)
- **Yahoo Finance** (free) — Stocks (AAPL), ETFs (SPY), crypto (BTC-USD), forex. **No API key needed.**
- **DexScreener** (free) — DEX pair data, no API key needed
- **CoinGecko** (free) — Broad crypto market data, rate-limited
- **Birdeye** (API key) — Solana on-chain data
- **Mock** (built-in) — Reproducible synthetic data for testing

### 📝 Decision Journal
Every agent decision is logged with full context — token, reasoning, confidence, risk metrics, and data sources. All stored as structured JSON.

---

## Architecture

```
src/kairos/
├── agents/           # 4 specialized AI agents
│   ├── base.py       # AgentBase abstract class
│   ├── research.py   # Market data collection
│   ├── quant.py      # Technical analysis
│   ├── risk.py       # Risk management (VaR, Kelly)
│   └── executor.py   # Final decision + journal
├── backtesting/      # Walk-forward engine
├── statistics/       # Bootstrap significance tests
├── strategies/       # Pre-built strategy configs
├── dashboard/        # Streamlit UI
├── data/             # Data providers + mock
├── indicators/       # Technical analysis (pure pandas)
└── cli/              # CLI interface
```

---

## Quick Examples

### Crypto (mock data, no API needed)
```bash
kairos demo
kairos backtest --strategy momentum --days 365
```

### Stocks (AAPL, SPY, etc. via Yahoo Finance)
```python
from kairos.backtesting.engine import WalkForwardEngine
from kairos.data.providers.yahoofinance import YahooFinanceProvider
import asyncio

async def run():
    provider = YahooFinanceProvider()
    df = await provider.fetch_price_data("AAPL", days=365*2)
    engine = WalkForwardEngine(df, train_size=90, test_size=30)
    result = engine.run({"buy_threshold": 65, "sell_threshold": 35})
    print(f"Sharpe: {result['aggregate']['sharpe_ratio']:.2f}")
    print(f"vs Benchmark: {result['benchmark']['sharpe_ratio']:.2f}")

asyncio.run(run())
```

## Example: Run a Backtest

```python
from kairos.backtesting.engine import WalkForwardEngine
from kairos.data.mock import MockDataProvider
from kairos.backtesting.metrics import PerformanceMetrics

# Load data
df = MockDataProvider.generate_price_data(days=365, seed=42)

# Run walk-forward backtest
engine = WalkForwardEngine(df, train_size=90, test_size=30)
result = engine.run({"buy_threshold": 65, "sell_threshold": 35})

# Check results
metrics = result["aggregate"]
print(f"Sharpe: {metrics['sharpe_ratio']}")
print(f"Return: {metrics['cumulative_return']:.2%}")
print(f"Max DD: {metrics['max_drawdown']:.2%}")
```

---

## Comparison

| | Kairos | Solana Agent Kit | NEXUS AI | AIVA |
|---|:------:|:----------------:|:--------:|:----:|
| Language | **Python** | TypeScript | Python | TypeScript |
| Transparency | **✅ Full trace** | ❌ | Partial | Trade logs |
| Backtesting | **✅ Walk-Forward** | ❌ | ❌ | ❌ |
| Bootstrap tests | **✅** | ❌ | ❌ | ❌ |
| Dashboard | **✅ Streamlit** | ❌ | ❌ | React |
| Data providers | **4 sources** | Solana only | Solana | Mock only |
| Strategy registry | **✅ 3 built-in** | ❌ | ❌ | ❌ |
| Open source | **✅ MIT** | Apache 2.0 | ❌ | MIT |

---

## Roadmap

- [x] Core agent framework (Research, Quant, Risk, Executor)
- [x] CLI + Streamlit Dashboard
- [x] Walk-Forward Backtesting Engine
- [x] Bootstrap Significance Testing
- [x] Multiple data providers (DexScreener, CoinGecko, Birdeye)
- [x] Strategy registry with 3 built-in strategies
- [ ] Real market data live trading mode
- [ ] Paper trading portfolio tracking
- [ ] Telegram/Discord bot integration
- [ ] Community strategy marketplace
- [ ] Jupyter Notebook tutorials

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

[MIT](LICENSE) © Derick Hu
