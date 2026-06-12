# Kairos 鈥?AI Trading Agents, Fully Transparent & Verifiable

<p align="center">
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python"></a>
  <a href="https://github.com/Electricitysheep/kairos/actions"><img src="https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?style=flat-square" alt="CI"></a>
  <a href="https://github.com/Electricitysheep/kairos/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square" alt="License"></a>
  <a href="https://pypi.org/project/kairos-agent/"><img src="https://img.shields.io/pypi/v/kairos-agent?style=flat-square&label=PyPI" alt="PyPI"></a>
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/github/stars/Electricitysheep/kairos?style=flat-square" alt="Stars"></a>
  <br>
  <a href="README.zh.md"><img src="https://img.shields.io/badge/Language-涓枃-E84D3D?style=flat-square" alt="涓枃"></a>
</p>

<p align="center">
  <b>AI Trading Agents, Fully Transparent &amp; Verifiable.</b>
  <br>
  <i>Research-grade agents for stocks, ETFs, and crypto 鈥?with full decision transparency.</i>
</p>

```text
鈹屸攢 Kairos Analyze 鈥?AAPL (stock) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€ Decision 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€ Indicators 鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹?鈹?BUY  (confidence: 50%)          鈹? 鈹?Composite Score  67/100鈹? 鈹?鈹?鈹?Composite score 67 above 65     鈹? 鈹?RSI(14)          73.3  鈹? 鈹?鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?Signal          BULLISH鈹? 鈹?鈹?鈹屸攢鈹€鈹€鈹€鈹€鈹€ AAPL Price Trend 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹?ADX              44.8  鈹? 鈹?鈹?鈹?$314.23  +26.92% over 90 bars   鈹?  鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹?鈹?鈻佲杺鈻冣枀鈻嗏枃鈻団枂鈻呪杽鈻冣杺鈻?(trend sparkline) 鈹?                             鈹?鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                             鈹?鈹?Research 鈫?Quant 鈫?Risk 鈫?Executor 鈥?every decision traceable    鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

**Not another black-box signal. Every decision comes with a complete, auditable reasoning trace.**

- **Transparent** 鈥?Watch your agent think in real-time via the Dashboard
- **Backtestable** 鈥?Walk-forward validation with statistical significance tests
- **Research-grade** 鈥?Bootstrap p-values, Sharpe ratios, drawdown analysis
- **Modular** 鈥?Extensible 4-agent architecture (Research, Quant, Risk, Executor)

---

## Quick Start

```bash
# 1. Install
pip install kairos-agent

# 2. Run a full demo with mock data (2 minutes, no API keys needed)
kairos demo

# 3. Launch the interactive Dashboard
kairos dashboard

# 4. Run a walk-forward backtest
kairos backtest --strategy momentum --days 365
```

---

## Why Kairos?

| Feature | Other AI Agents | **Kairos** |
|---------|----------------|------------|
| See agent's reasoning | 鉂?Black box | 鉁?Full reasoning trace |
| Backtest strategies | 鉂?Can't test | 鉁?Walk-forward validation |
| Statistical significance | 鉂?"Trust me" | 鉁?Bootstrap p-value |
| Interactive dashboard | 鉂?CLI only | 鉁?Streamlit UI |
| Pre-built strategies | 鉂?None | 鉁?3 built-in strategies |
| Real market data | 鉂?Mock only | 鉁?**5 sources** (stocks, crypto, ETFs) |
| Benchmark comparison | 鉂?None | 鉁?Buy-and-hold benchmark |
| Pythonic API | 鉂?TypeScript | 鉁?Python 3.10+ |
| Modular agents | 鉂?Monolithic | 鉁?4 specialized agents |

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

### 馃 Multi-Agent Architecture

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? Orchestrator                                       鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹?鈹?鈹? 鈹?Research 鈹傗啋 鈹? Quant   鈹傗啋 鈹? Risk    鈹傗啋 鈹侲xec 鈹?鈹?鈹? 鈹? Agent   鈹? 鈹? Agent   鈹? 鈹? Agent   鈹? 鈹倁tor 鈹?鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹?鈹?鈹?      鈹?             鈹?            鈹?         鈹?     鈹?鈹? Market Data    TA Indicators  VaR/Kelly   Decision 鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

### 馃搳 Real-Time Dashboard
Monitor agent reasoning, technical indicators, risk metrics, and decision history in an interactive Streamlit dashboard.

### 馃搱 Walk-Forward Backtesting
Statistically rigorous backtesting with rolling windows, embargo gaps, and comprehensive performance metrics.

### 馃敩 Bootstrap Significance Tests
Don't trust your backtest results? Kairos computes p-values and confidence intervals to tell you if your strategy is statistically significant.

### 馃敆 Multiple Data Sources (Stocks, Crypto, ETFs)
- **Yahoo Finance** (free) 鈥?Stocks (AAPL), ETFs (SPY), crypto (BTC-USD), forex. **No API key needed.**
- **DexScreener** (free) 鈥?DEX pair data, no API key needed
- **CoinGecko** (free) 鈥?Broad crypto market data, rate-limited
- **Birdeye** (API key) 鈥?Solana on-chain data
- **Mock** (built-in) 鈥?Reproducible synthetic data for testing

### 馃摑 Decision Journal
Every agent decision is logged with full context 鈥?token, reasoning, confidence, risk metrics, and data sources. All stored as structured JSON.

---

## Architecture

```
src/kairos/
鈹溾攢鈹€ agents/           # 4 specialized AI agents
鈹?  鈹溾攢鈹€ base.py       # AgentBase abstract class
鈹?  鈹溾攢鈹€ research.py   # Market data collection
鈹?  鈹溾攢鈹€ quant.py      # Technical analysis
鈹?  鈹溾攢鈹€ risk.py       # Risk management (VaR, Kelly)
鈹?  鈹斺攢鈹€ executor.py   # Final decision + journal
鈹溾攢鈹€ backtesting/      # Walk-forward engine
鈹溾攢鈹€ statistics/       # Bootstrap significance tests
鈹溾攢鈹€ strategies/       # Pre-built strategy configs
鈹溾攢鈹€ dashboard/        # Streamlit UI
鈹溾攢鈹€ data/             # Data providers + mock
鈹溾攢鈹€ indicators/       # Technical analysis (pure pandas)
鈹斺攢鈹€ cli/              # CLI interface
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
| Transparency | **鉁?Full trace** | 鉂?| Partial | Trade logs |
| Backtesting | **鉁?Walk-Forward** | 鉂?| 鉂?| 鉂?|
| Bootstrap tests | **鉁?* | 鉂?| 鉂?| 鉂?|
| Dashboard | **鉁?Streamlit** | 鉂?| 鉂?| React |
| Data providers | **4 sources** | Solana only | Solana | Mock only |
| Strategy registry | **鉁?3 built-in** | 鉂?| 鉂?| 鉂?|
| Open source | **鉁?MIT** | Apache 2.0 | 鉂?| MIT |

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

[MIT](LICENSE) 漏 Derick Hu
