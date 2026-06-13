# Kairos -- AI Trading Agents, Fully Transparent & Verifiable

<p align="center">
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python"></a>
  <a href="https://github.com/Electricitysheep/kairos/actions"><img src="https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?style=flat-square" alt="CI"></a>
  <a href="https://github.com/Electricitysheep/kairos/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square" alt="License"></a>
  <a href="https://github.com/Electricitysheep/kairos/stargazers"><img src="https://img.shields.io/github/stars/Electricitysheep/kairos?style=flat-square" alt="Stars"></a>
  <br>
  <b><a href="README.zh.md">中文</a> | English</b>
</p>

---

## Quick Start

```bash
pip install git+https://github.com/Electricitysheep/kairos.git
kairos analyze AAPL
```

## Why Kairos?

Most crypto AI agents are black boxes. Kairos gives you **complete decision transparency** --
every signal comes with a full reasoning trace, Walk-Forward backtesting, and Bootstrap
statistical significance tests.

## Features

- **5 AI Agents**: Research, Quant, Risk, Sentiment, Executor
- **Walk-Forward Backtesting**: Academic-grade rolling window validation
- **Bootstrap Statistics**: p-values and confidence intervals
- **Strategy Plugin System**: Write custom strategies as Python classes
- **6 Built-in Strategies**: momentum, mean_reversion, conservative, rsi, bb, ensemble
- **Paper + Live Trading**: Via Alpaca (free paper trading)
- **HTML Reports**: One-click research report generation

## CLI Commands

| Command | Description |
|---------|-------------|
| kairos analyze AAPL | Real-time stock/crypto analysis |
| kairos leaderboard AAPL | Strategy ranking |
| kairos backtest --token MSFT | Walk-Forward backtest |
| kairos paper AAPL --qty 10 | Paper trading via Alpaca |
| kairos report AAPL | HTML research report |
| kairos dashboard | Interactive Streamlit dashboard |
| kairos demo | Zero-friction demo |

## License

MIT - Zhou Yuchen
