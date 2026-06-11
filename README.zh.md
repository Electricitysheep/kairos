# Kairos — 透明可验证的 AI 交易 Agent 框架

<p align="center">
  <a href="https://github.com/Electricitysheep/kairos"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python"></a>
  <a href="https://github.com/Electricitysheep/kairos/actions"><img src="https://img.shields.io/github/actions/workflow/status/Electricitysheep/kairos/ci.yml?style=flat-square" alt="CI"></a>
  <a href="https://github.com/Electricitysheep/kairos/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Electricitysheep/kairos?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <b>面向量化开发者的 AI Agent 框架 — 完全透明、可回测、可验证。</b>
  <br>
  <i>古希腊语中，Kairos (καιρός) 意为"关键恰当时刻"——信号与执行之间的那个瞬间。</i>
</p>

---

## 是什么？

大多数加密货币和股票的 AI 交易工具是**黑盒**——它们给你信号，但不告诉你为什么。

Kairos 反过来：**每个决策都附带完整的、可审计的推理链。**

```text
┌─ Kairos Analyze — AAPL (股票) ──────────────────────────────────┐
│ ┌─────────── 决策 ───────────┐  ┌────── 技术指标 ──────────┐  │
│ │ BUY  (置信度: 50%)          │  │ Composite Score  67/100│  │
│ │ Composite score 67 超过阈值 65│  │ RSI(14)          73.3  │  │
│ └──────────────────────────────┘  │ Signal          BULLISH│  │
│ ┌────── AAPL 价格趋势 ─────────┐  │ ADX              44.8  │  │
│ │ $314.23  +26.92% 近 90 个周期 │   └──────────────────────┘  │
│ └──────────────────────────────┘                              │
│ 5个 AI Agent 流水线 — 每个决策都可追溯                          │
└────────────────────────────────────────────────────────────────┘
```

---

## 快速开始

```bash
# 1. 安装
pip install kairos

# 2. 分析一只股票
kairos analyze AAPL

# 3. 回测验证
kairos backtest --token MSFT --days 730

# 4. 多策略排行榜
kairos leaderboard AAPL
```

---

## 核心特性

| 特性 | 说明 |
|:-----|:------|
| **5 个专业 AI Agent** | Research → Quant → Risk → Sentiment → Executor |
| **Walk-Forward 回测** | 学术级滚动窗口验证，防止过拟合 |
| **Bootstrap 统计检验** | 计算 p-value 和置信区间，判断策略是否统计显著 |
| **策略插件系统** | 自定义 Strategy 类，像写 Python 一样写策略 |
| **6 个内建策略** | momentum/mean_reversion/conservative/rsi/bb/ensemble |
| **6 个数据源** | Yahoo Finance、FRED、DexScreener、CoinGecko、Birdeye、Mock |
| **Alpaca 交易** | 纸上交易 + 实盘交易（免费） |
| **HTML 研究报告** | 一键生成可分享的研究报告 |
| **多时间框架** | 15分钟/1小时/1天信号融合 |
| **策略优化器** | 网格搜索最优参数 |
| **MIT 许可证** | 商业友好，完全开源 |

---

## CLI 命令

| 命令 | 说明 |
|:-----|:------|
| `kairos analyze AAPL` | 实时分析股票/加密货币 |
| `kairos leaderboard AAPL` | 所有策略排名对比 |
| `kairos backtest --token MSFT` | Walk-Forward 回测 |
| `kairos compare AAPL` | 多策略同屏对比 |
| `kairos paper AAPL --qty 10` | 纸上交易 |
| `kairos report AAPL` | HTML 研究报告 |
| `kairos dashboard` | 交互式 Dashboard |
| `kairos demo` | 零门槛演示 |

---

## 为什么选择 Kairos？

| 对比项 | 其他 AI Agent | **Kairos** |
|:-------|:-------------|:-----------|
| 推理透明 | ❌ 黑盒 | ✅ 完整推理链 |
| 回测验证 | ❌ 无法回测 | ✅ Walk-Forward 验证 |
| 统计检验 | ❌ "相信我" | ✅ Bootstrap p-value |
| 交互式面板 | ❌ 仅命令行 | ✅ Streamlit UI |
| 策略插件 | ❌ 固定逻辑 | ✅ 自定义 Strategy 类 |
| 实盘交易 | ❌ 仅模拟 | ✅ Alpaca 集成 |
| 股票+加密货币 | ❌ 仅其一 | ✅ 两者都支持 |
| 开源许可 | ❌ 限制性 | ✅ MIT 完全自由 |

---

## 自定义策略示例

```python
from kairos.strategies.base import Strategy, StrategyContext, Signal
from kairos.strategies.registry import StrategyRegistry

class MyStrategy(Strategy):
    def compute_signal(self, ctx: StrategyContext) -> Signal:
        prices = ctx.prices
        if len(prices) < 2:
            return Signal.hold()
        if prices.iloc[-1] > prices.iloc[-2]:
            return Signal.buy(confidence=0.6, reason="价格上涨")
        return Signal.hold()

# 注册到系统
registry = StrategyRegistry()
registry.register_class("my_strat", MyStrategy)
```

---

## 架构

```
src/kairos/
├── agents/         # 5 个 AI Agent
├── backtesting/    # Walk-Forward 回测 + 优化器
├── brokers/        # Alpaca 交易接口
├── cli/            # 命令行界面 (11 个命令)
├── core/           # 核心编排器 + 日志
├── dashboard/      # Streamlit 可视化面板
├── data/           # 6 个数据源
├── indicators/     # 纯 pandas 技术指标
├── statistics/     # Bootstrap 统计检验
└── strategies/     # 策略基类 + 6 个内建策略
```

---

## 路线图

- [x] 5-Agent 流水线 (Research, Quant, Risk, Sentiment, Executor)
- [x] Walk-Forward 回测引擎
- [x] Bootstrap 显著性检验
- [x] 策略插件系统
- [x] 6 个内建策略
- [x] Yahoo Finance + FRED 数据源
- [x] Alpaca 纸上/实盘交易
- [x] HTML 研究报告生成
- [x] 策略排行榜
- [ ] PyPI 发布
- [ ] Telegram Bot 通知
- [ ] 社区策略市场

---

## 许可证

[MIT](LICENSE) © Zhou Yuchen
