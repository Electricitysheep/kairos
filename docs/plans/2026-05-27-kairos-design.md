# Kairos Design Document

> **AI Trading Agents, Fully Transparent & Verifiable**

**Created**: 2026-05-27
**Status**: Draft → Approved
**Author**: Derick Hu

---

## 1. Brand & Vision

### 1.1 Name & Meaning

**Kairos** (καιρός) — Ancient Greek word meaning "the right, critical, or opportune moment."

In ancient Greek, *chronos* (χρόνος) is chronological, sequential time — the clock ticking.
*Kairos* (καιρός) is the qualitative moment — the instant between signal and action where opportunity lives.

For trading: *Kairos is the moment between signal and execution.*

### 1.2 Tagline

> **Kairos — AI Trading Agents, Fully Transparent & Verifiable**

### 1.3 One-Sentence Positioning

The first open-source framework for building **transparent, backtestable, statistically-validated** AI trading agents — starting with crypto markets.

### 1.4 Target Audience

| Priority | Audience | Pain Point | Why Kairos |
|:--------:|----------|------------|------------|
| 1 | Quant researchers / Data scientists | Need AI-powered crypto analysis but can't verify existing tools | Every decision comes with a complete reasoning trace + statistical validation |
| 2 | ML/CS students (grad school apps) | Need a project that shows AI + quant + engineering | Multi-agent LLM architecture + rigorous backtesting + clean Python code |
| 3 | Crypto traders / investors | Tired of black-box signals with no accountability | Full decision transparency — see exactly why the agent made each call |

### 1.5 Success Criteria

| Metric | 6-Month Target | 12-Month Target |
|--------|:--------------:|:----------------:|
| GitHub Stars | 300-800 | 1,000-3,000 |
| pip installs | 1,000+ | 10,000+ |
| Contributors | 5+ | 20+ |
| Awesome List inclusions | 2+ | 5+ |
| Hacker News front page | 1x | 2x |
| YouTube demos | 1 | 3+ |

---

## 2. Core Differentiation

### 2.1 Comparison: Kairos vs. Existing Projects

| Dimension | Solana Agent Kit | NEXUS AI | AIVA | PyHedge | **Kairos** |
|-----------|:--------------:|:--------:|:----:|:-------:|:----------:|
| Language | TypeScript | Python | TypeScript | Python | **Python** |
| Agent transparency | ❌ | Partial | ✅ Trade logs | ❌ | **✅ Full reasoning trace** |
| Backtesting engine | ❌ | ❌ | ❌ | ✅ Basic | **✅ Walk-Forward + Bootstrap** |
| Statistical validation | ❌ | ❌ | ❌ | ❌ | **✅ Significance tests** |
| Modular agent framework | ❌ Tool kit | ✅ Fixed 4-agent | ✅ Fixed | ✅ 10 agents | **✅ Pluggable agent architecture** |
| Research report output | ❌ | ❌ | ❌ | ❌ | **✅ PDF/Markdown reports** |
| Decision transparency dashboard | ❌ | ❌ | ❌ | ❌ | **✅ Real-time agent reasoning view** |
| Jupyter Notebook support | ❌ | ❌ | ❌ | ❌ | **✅ Interactive research notebooks** |

### 2.2 Core Philosophy

> **Most crypto AI agents are black boxes. They take your money, make decisions, and give you no window into their reasoning.**
>
> Kairos inverts this: every decision comes with a complete paper trail. You can see what data it consulted, why it reached that conclusion, how confident it was, and what risk it calculated — all before execution.

---

## 3. Architecture

### 3.1 Multi-Agent System

```
User Input (token address / question)
         │
         ▼
┌─────────────────────┐
│  Orchestrator Agent │  ← Routes requests, manages state, handles errors
└──────┬──────┬───────┘
       │      │
       ▼      ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Research │ │   Quant  │ │   Risk   │ │Executor  │
│  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │
├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤
│ • On-chain│ │ • TA     │ │ • VaR    │ │ • Paper  │
│ • News    │ │ • Factors│ │ • Kelly  │ │ • Live   │
│ • Social  │ │ • Signals│ │ • DD cap │ │ • Logging│
│ • Price   │ │ • Score  │ │ • Circuit│ │ • Report │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
       │           │           │            │
       └───────────┴───────────┴────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│     Decision with Reasoning Trace   │
│  { confidence, reasoning, risk,     │
│    data_sources, decision }          │
└─────────────────────────────────────┘
```

### 3.2 Agent Responsibilities

#### Orchestrator Agent
- Receives user input and routes to appropriate agents
- Aggregates responses into structured output
- Manages conversation state and error recovery
- Generates final decision with complete trace

#### Research Agent (Data Collection)
- Fetches on-chain data (Birdeye: price, OHLCV, transactions)
- Fetches market data (DexScreener: pairs, liquidity, volume)
- Fetches on-chain analytics (Helius: transfers, whale activity)
- Fetches news/sentiment (CryptoPanic / social feeds)
- Outputs: structured data packet with all raw signals

#### Quant Agent (Analysis)
- Computes technical indicators (RSI, MACD, Bollinger, EMA cross, ADX)
- Computes on-chain metrics (holder concentration, whale flow, velocity)
- Computes factor scores (momentum, volatility, volume profile)
- Applies statistical tests (significance, regime detection)
- Outputs: quantitative signal with confidence levels

#### Risk Agent (Risk Management)
- Calculates position sizing via Kelly criterion
- Computes Value at Risk (VaR) and expected shortfall
- Applies drawdown limits and circuit breakers
- Validates against portfolio-level constraints
- Outputs: risk-adjusted position recommendation

#### Executor Agent (Decision & Execution)
- Aggregates signals from Research + Quant + Risk
- Generates final BUY/SELL/HOLD decision with rationale
- Simulates execution (paper trading) for backtesting
- Logs complete decision trace to journal
- (Future) Real execution via Jupiter API

### 3.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Language** | Python 3.10+ | ML/quant ecosystem, user's expertise |
| **Agent Framework** | Custom (lightweight) | Avoid heavy dependencies, full control |
| **LLM Integration** | OpenAI / Claude API (BYOK) | Agent reasoning and decision-making |
| **Data - Market** | Birdeye API, DexScreener, CoinGecko | Token prices, OHLCV, pairs |
| **Data - On-chain** | Helius, Solana RPC | Transactions, holders, whale tracking |
| **Technical Analysis** | pandas-ta, TA-Lib | 130+ technical indicators |
| **Backtesting** | Custom (vectorized + event-driven) | Walk-forward with statistical validation |
| **Stats** | NumPy, SciPy, statsmodels | Bootstrap tests, significance, HMM |
| **Dashboard** | Streamlit | Real-time agent reasoning visualization |
| **Reports** | Jinja2 + LaTeX/Markdown | Research report generation |
| **Package** | Poetry / pip | Modern Python packaging |
| **Testing** | pytest | Unit + integration tests |
| **CI/CD** | GitHub Actions | Auto-testing, linting |
| **Storage** | SQLite + JSON | Decision journal + config |

---

## 4. Viral-Worthy Features

### 4.1 Agent Reasoning Dashboard (Primary Viral Feature)

A Streamlit dashboard showing the AI agent's complete thought process in real-time.

**What it displays:**
- Agent's current reasoning (streaming text, like an LLM)
- Data sources consulted (with timestamps)
- Technical indicators visualized as charts
- Confidence score with explanation
- Risk metrics (VaR, Kelly fraction, drawdown limit)
- Final decision with full rationale
- Historical decision timeline

**Why this drives stars:** No other crypto AI agent shows its thinking. This is screenshot-worthy, tweet-worthy, and demonstrates the "transparency" promise instantly.

### 4.2 One-Click Demo

```bash
pip install kairos
kairos demo
```

The `demo` command:
1. Generates realistic mock market data
2. Runs a complete agent analysis cycle
3. Shows the reasoning dashboard
4. Outputs a sample decision journal
5. Takes < 2 minutes end-to-end

### 4.3 Research Report Generator

```bash
kairos research SOL --format pdf
```

Generates an institutional-grade research report:
1. Executive summary
2. Market overview (price action, volume, volatility)
3. Technical analysis (indicators, patterns, regime)
4. On-chain analysis (holders, whales, flow)
5. AI Agent assessment (reasoning, confidence, risk)
6. Risk metrics (VaR, drawdown, position sizing)
7. References and methodology

*Output format: PDF (LaTeX engine) and Markdown*

### 4.4 Decision Transparency Journal

Every agent decision is logged as a structured JSON record:

```json
{
  "timestamp": "2026-05-27T10:00:00Z",
  "token": "SOL/USDT",
  "decision": "BUY",
  "confidence": 0.72,
  "reasoning_summary": "Bullish RSI divergence, volume confirmation, whale accumulation detected",
  "data_sources": ["birdeye_price", "helius_transfers", "pandas_ta"],
  "research_agent": {
    "price": { "current": 145.20, "sma_20": 138.50, "sma_50": 132.00 },
    "volume": { "24h": 3200000000, "change_24h": 0.25 },
    "onchain": { "whale_net_flow": 1250000, "holder_change_7d": 0.03 }
  },
  "quant_agent": {
    "rsi_14": 58.3,
    "macd": { "signal": "bullish_cross", "histogram": 1.2 },
    "bb_position": "middle_to_upper",
    "composite_score": 72.5
  },
  "risk_agent": {
    "var_95": 0.042,
    "kelly_fraction": 0.15,
    "position_cap": 500,
    "circuit_breaker": "inactive"
  },
  "final_action": {
    "type": "BUY",
    "size_usd": 75.0,
    "max_slippage": 0.003,
    "stop_loss": 138.00
  }
}
```

This journal is what makes the agent **verifiable** — every decision can be audited.

### 4.5 Compare Mode

```bash
kairos compare --agents momentum,mean_reversion,llm
```

Runs multiple agent strategies side-by-side:
- Visual comparison of decisions over time
- Performance metrics (if in paper trading mode)
- Agreement/disagreement analysis
- Risk-return scatter plot

---

## 5. Phase Plan (6-12 Months)

### Phase 1: Foundation (Months 1-2) — Target: 50-100 ⭐

| Task | Details |
|------|---------|
| Project scaffold | Package structure, pyproject.toml, CI/CD |
| Core agent framework | Agent base class, orchestrator, pipeline |
| Research Agent | Birdeye + DexScreener + CoinGecko integration |
| Quant Agent | pandas-ta indicators + composite scoring |
| Risk Agent | Kelly criterion, VaR, position sizing |
| Executor Agent | Decision aggregation + JSON journal |
| `kairos demo` command | CLI with mock data, full pipeline demo |
| Decision journal | Structured logging for all agent outputs |
| README v1 | Problem → GIF → Install → Use Cases |
| Initial tests | pytest for all core modules |

### Phase 2: Transparency (Months 2-3) — Target: 100-300 ⭐

| Task | Details |
|------|---------|
| Streamlit Dashboard | Real-time agent reasoning visualization |
| `kairos dashboard` command | Launch the dashboard locally |
| `kairos analyze <token>` command | Real data analysis (with API keys) |
| Decision trace UI | Timeline view of past decisions |
| Confidence visualization | Charts showing confidence over time |
| Data source integration | Helius on-chain data, news feeds |
| Jupyter Notebook | Interactive research notebook |
| README v2 | Add dashboard screenshots, comparison table |

### Phase 3: Research & Reports (Months 3-5) — Target: 200-500 ⭐

| Task | Details |
|------|---------|
| `kairos research <token>` command | Generate research reports |
| LaTeX report engine | Professional PDF report generation |
| Markdown report engine | Lighter-weight report format |
| Walk-Forward backtesting | Backtest agent strategies over time |
| Bootstrap significance tests | Statistical validation of agent decisions |
| Comparison table generation | Multi-strategy analysis |
| Example strategies | 3 pre-built agent strategies |
| Documentation site | GitHub Pages with full docs |
| `kaeros compare` command | Side-by-side strategy comparison |

### Phase 4: Launch & Community (Months 5-6) — Target: 300-800 ⭐

| Task | Details |
|------|---------|
| Hacker News launch | Prepare Show HN post + story |
| YouTube demo video | Screen recording of dashboard |
| r/algotrading post | Use-case demonstration |
| Awesome List submissions | awesome-quant, awesome-crypto-trading |
| Issue templates | GitHub issue/PR templates |
| Contributing guide | CONTRIBUTING.md |
| Code of conduct | Community guidelines |
| Blog post #1 | "Building Transparent AI Trading Agents" |

### Phase 5: Growth (Months 6-12) — Target: 800-3,000 ⭐

| Task | Details |
|------|---------|
| Paper trading mode | Simulated portfolio tracking |
| Agent strategy marketplace | Community-submitted strategies |
| Multi-timeframe analysis | 15m, 1h, 4h, 1d signals |
| Telegram / Discord bot | Agent alerts via chat |
| GitHub Actions weekly report | Auto-generated market analysis |
| Blog post #2 | Architecture deep-dive |
| Blog post #3 | Comparison: Kairos vs other agents |
| PR outreach | Engage with crypto Twitter / YouTube |
| Performance optimizations | Async data fetching, caching |

---

## 6. README Structure (Star-Optimized)

```
# Kairos — AI Trading Agents, Fully Transparent & Verifiable

<p align="center">
  [Badges: Python, CI, License, Stars, pip]
</p>

<p align="center">
  <img src="assets/dashboard_demo.gif" alt="Kairos Dashboard Demo" width="800">
  <br>
  <em>See exactly what your AI agent is thinking, in real-time</em>
</p>

---

pip install kairos && kairos demo

---

## Why Kairos?

[Comparison Table: Kairos vs Other AI Agents]

| Feature | Other AI Agents | Kairos |
|---------|----------------|--------|
| See agent's reasoning | ❌ Black box | ✅ Full thought process |
| Backtest strategies | ❌ Can't test | ✅ Walk-forward validation |
| Statistical proof | ❌ "Trust me" | ✅ Significance tests |
| Generate reports | ❌ No | ✅ PDF reports |
| Visual dashboard | ❌ CLI only | ✅ Streamlit UI |

## Quick Start (2 minutes)

## Features

[With GIFs/screenshots for each]

## Use Cases

## Architecture

## Roadmap

## Contributing

## License
```

---

## 7. Launch Strategy

### Phase 1: Hacker News (Day 1)

**Title**: "Show HN: I got tired of black-box crypto AI agents, so I built one you can actually verify"

**Story angle**: Personal frustration → built a solution → technical details → results

**Timing**: Tuesday 8AM EST

### Phase 2: Reddit (Day 2-3)

**Subreddits**: r/algotrading, r/cryptocurrency, r/MachineLearning

**Content**: Demo video + comparison table + "what makes Kairos different"

### Phase 3: YouTube (Week 1-2)

**Video**: 10-min screen recording: "I asked an AI agent to analyze SOL — here's what it showed me"

**Content**: Walk through the dashboard, show agent's reasoning, discuss transparency

### Phase 4: Product Hunt (Week 2-3)

**Product Hunt launch**: Polished version with all features working

### Phase 5: Blog (Month 1-2)

**Blog post 1**: "Building Transparent AI Trading Agents: Why I Open-Sourced Kairos"
**Blog post 2**: "Kairos Architecture: How We Built a Verifiable AI Trading Agent"
**Blog post 3**: "Kairos vs The Market: Benchmarking AI Agents Against HODL"

---

## 8. Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|:------:|:-----------:|------------|
| Python crypto ecosystem less mature | Medium | High | Use REST APIs (Birdeye/Helius) not complex SDKs |
| Competition from TypeScript projects | Medium | High | Python ecosystem is less crowded — focus on quality |
| "Another trading bot" fatigue | High | Medium | Clear differentiation via transparency positioning |
| Low star growth | Medium | Medium | Launch wave strategy + YouTube demo |
| API costs for real data | Low | High | BYOK model, free tier APIs, mock data default |
| LLM API costs for reasoning | Low | Medium | BYOK, configurable model selection |
