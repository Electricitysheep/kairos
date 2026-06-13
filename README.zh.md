# Kairos — 透明可验证的 AI 交易 Agent 框架

<p align="center">
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&amp;logo=python" alt="Python"></a>
  <a href="https://github.com/Electricitysheep/kairos/actions"><img src="https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?style=flat-square" alt="CI"></a>
  <a href="https://github.com/Electricitysheep/kairos/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square" alt="License"></a>
  <br>
  <b><a href="README.md">English</a> | 中文</b>
</p>

---

## Kairos 是什么？

Kairos 是一个开源 Python 框架，用于构建透明、可验证的 AI 交易 Agent。

不同于其他黑盒子信号，Kairos 的每个决策都附带完整的推理链和统计验证。

## 快速开始

```bash
pip install git+https://github.com/Electricitysheep/kairos.git
kairos analyze AAPL
```

## 命令一览

| 命令 | 说明 |
|:-----|:------|
| kairos analyze AAPL | 实时分析股票/加密货币 |
| kairos leaderboard AAPL | 策略排行榜 |
| kairos backtest --token MSFT | Walk-Forward 回测 |
| kairos paper AAPL --qty 10 | 纸上交易 |
| kairos report AAPL | HTML 研究报告 |
| kairos dashboard | 交互式 Dashboard |
| kairos demo | 零门槛演示 |

## 核心特性

- **5 个专业 AI Agent**: Research → Quant → Risk → Sentiment → Executor
- **Walk-Forward 回测**: 学术级滚动窗口验证
- **Bootstrap 统计检验**: p-value 和置信区间
- **策略插件系统**: 自定义 Strategy 类
- **6 个内建策略**: momentum/mean_reversion/conservative/rsi/bb/ensemble
- **Alpaca 交易**: 纸上交易 + 实盘交易
- **HTML 研究报告**: 一键生成可分享的报告

## 开发计划

- [x] 5-Agent 流水线
- [x] Walk-Forward 回测引擎
- [x] Bootstrap 显著性检验
- [x] 策略插件系统
- [x] 6 个内建策略
- [x] Alpaca 纸上/实盘交易
- [x] HTML 研究报告
- [ ] PyPI 发布
- [ ] Telegram Bot 通知

## 许可证

MIT © Zhou Yuchen
