<div align="center">

# Kairos

**透明可验证的 AI 交易 Agent 框架**

*首个用于构建「透明、可回测、经统计验证」的 AI 交易 Agent 的开源框架。*

[![PyPI](https://img.shields.io/pypi/v/kairos-agent?style=flat-square)](https://pypi.org/project/kairos-agent/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://www.python.org/downloads/)
[![CI](https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?branch=master&style=flat-square)](https://github.com/Electricitysheep/kairos/actions)
[![License: MIT](https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Electricitysheep/kairos?style=flat-square)](https://github.com/Electricitysheep/kairos/stargazers)

[English](README.md) · [中文](README.zh.md)

</div>

---

## 为什么是 Kairos？

大多数 AI 交易工具都是**黑箱**——只给信号，不给逻辑。Kairos 反其道而行：**每个决策都是确定性的、透明且可验证的。**

- 🔍 **决策完全可审计** —— 5 个 Agent 都是规则化的（无 LLM、无隐藏模型），每一步都记录做出该判断的确切依据。
- 📈 **Walk-Forward 回测** —— 学术级滚动窗口样本外验证，而非过拟合式曲线拟合。
- 🧪 **Bootstrap 统计检验** —— 用 p-value 和置信区间判断优势是真实的还是噪声。

> *Kairos*（καιρός）—— 古希腊语，意为「关键的时刻」：信号与执行之间、机会所在的那一瞬。

## 快速开始

```bash
pip install git+https://github.com/Electricitysheep/kairos.git
kairos demo          # 零配置演示，无需 API key
kairos analyze AAPL  # 实时股票 / 加密货币分析
```

`kairos demo` 会在样例数据上完整运行 5-Agent 流水线，无需任何配置。

## 核心特性

- **5 个规则化 Agent** —— Research → Quant → Risk → Sentiment → Executor，作为协同流水线运行
- **Walk-Forward 回测引擎** —— 滚动窗口样本外验证
- **Bootstrap 统计检验** —— 策略收益的 p-value 与置信区间
- **策略插件系统** —— 用普通 Python 类编写自定义策略
- **6 个内建策略** —— momentum, mean_reversion, conservative, rsi, bb, ensemble
- **纸上 + 实盘交易** —— 通过 Alpaca（免费纸上交易）
- **HTML 研究报告** —— 一键生成可分享报告
- **6 个数据源** —— Yahoo Finance, FRED, CoinGecko, DexScreener, Birdeye, Mock

## 命令列表

| 命令 | 说明 |
|:-----|:------|
| `kairos demo` | 零门槛演示（无需 API key） |
| `kairos analyze AAPL` | 实时分析股票 / 加密货币 |
| `kairos leaderboard AAPL` | 策略排行榜 |
| `kairos backtest --token AAPL` | Walk-Forward 回测 |
| `kairos compare AAPL MSFT` | 多标的对比 |
| `kairos report AAPL` | 生成 HTML 研究报告 |
| `kairos paper AAPL --qty 10` | Alpaca 纸上交易 |
| `kairos live AAPL --qty 10` | Alpaca 实盘交易 |
| `kairos dashboard` | 交互式 Dashboard |

## 用 Docker 运行

```bash
docker build -t kairos .
docker run -p 8501:8501 kairos       # dashboard 访问 http://localhost:8501
docker run kairos analyze AAPL       # 或运行任意 CLI 命令
```

## 架构

五个专职 Agent 由 `Orchestrator` 编排为顺序流水线，每个 Agent 输出结构化结果，完整链路写入决策日志。

```
Research ─▶ Quant ─▶ Risk ─▶ Sentiment ─▶ Executor
   │          │        │          │           │
   └──────────┴────────┴──────────┴───────────┘
                       ▼
             决策日志（完整决策链路）
```

## 自定义策略示例

```python
from kairos.strategies.base import Strategy, StrategyContext, Signal

class MyStrategy(Strategy):
    def compute_signal(self, ctx: StrategyContext) -> Signal:
        price = ctx.latest()
        if price > self.config.get("threshold", 100):
            return Signal.buy(confidence=0.7, reason=f"价格 {price:.2f} 高于阈值")
        return Signal.hold()
```

注册后即自动出现在 `kairos leaderboard` 与 `kairos backtest` 中。完整示例见 [`examples/custom_strategy.py`](examples/custom_strategy.py) 与 [`notebooks/01_kairos_quickstart.ipynb`](notebooks/01_kairos_quickstart.ipynb)。

## 贡献

欢迎贡献，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。适合上手：新增策略、新增数据源、改进文档。

## 免责声明

Kairos 是研究与教育工具，**不构成投资建议**。交易有亏损风险，请先使用纸上交易，切勿投入无法承受损失的资金。

## 许可证

[MIT](LICENSE) © Zhou Yuchen
