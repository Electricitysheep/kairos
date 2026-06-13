# Kairos -- 透明可验证的 AI 交易 Agent 框架

<p align="center">
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python"></a>
  <a href="https://github.com/Electricitysheep/kairos/actions"><img src="https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?style=flat-square" alt="CI"></a>
  <a href="https://github.com/Electricitysheep/kairos/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square" alt="License"></a>
  <br>
  <b>中文 | <a href="README.md">English</a></b>
</p>

---

## 快速开始

```bash
pip install git+https://github.com/Electricitysheep/kairos.git
kairos analyze AAPL
```

## 核心特性

- **5 个 AI Agent**: Research, Quant, Risk, Sentiment, Executor
- **Walk-Forward 回测引擎**: 学术级滚动窗口验证
- **Bootstrap 统计检验**: p-value 和置信区间
- **策略插件系统**: 自定义 Strategy 类
- **6 个内建策略**: momentum, mean_reversion, conservative, rsi, bb, ensemble
- **Alpaca 交易**: 纸上交易 + 实盘交易
- **HTML 研究报告**: 一键生成可分享的报告

## 命令列表

| 命令 | 说明 |
|:-----|:------|
| kairos analyze AAPL | 实时分析股票/加密货币 |
| kairos leaderboard AAPL | 策略排行榜 |
| kairos backtest --token MSFT | Walk-Forward 回测 |
| kairos paper AAPL --qty 10 | Alpaca 纸上交易 |
| kairos report AAPL | HTML 研究报告 |
| kairos dashboard | 交互式 Dashboard |
| kairos demo | 零门槛演示 |

## 许可证

MIT - Zhou Yuchen
