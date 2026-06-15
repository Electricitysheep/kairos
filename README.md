# Kairos

AI Trading Agents, Fully Transparent &amp; Verifiable

## Why Kairos?

Most AI trading agents are black boxes. They give signals without showing their reasoning.
Kairos changes that. Every decision comes with a complete reasoning trace,
Walk-Forward backtesting, and Bootstrap statistical significance tests.

### Install & Try

```bash
pip install git+https://github.com/Electricitysheep/kairos.git
kairos analyze AAPL
```

## Features

- **5 AI Agents**: Research, Quant, Risk, Sentiment, Executor
- **Walk-Forward Backtesting**: Academic-grade rolling window validation
- **Bootstrap Statistics**: p-values and confidence intervals
- **Strategy Plugin System**: Write custom strategies as Python classes
- **6 Built-in Strategies**: momentum, mean_reversion, conservative, rsi, bb, ensemble
- **Paper + Live Trading**: Via Alpaca (free paper trading)
- **HTML Reports**: One-click research report generation
- **6 Data Sources**: Yahoo Finance, FRED, CoinGecko, DexScreener, Birdeye, Mock

## CLI Commands

| Command | Description |
|---------|-------------|
| kairos analyze AAPL | Real-time stock/crypto analysis |
| kairos leaderboard AAPL | Rank all 6 strategies by performance |
| kairos backtest | Walk-Forward backtesting |
| kairos paper AAPL --qty 10 | Paper trading via Alpaca |
| kairos report AAPL | Generate HTML research report |
| kairos dashboard | Launch interactive dashboard |
| kairos demo | Zero-friction demo |

## Custom Strategy Example

```python
from kairos.strategies.base import Strategy, StrategyContext, Signal

class MyStrategy(Strategy):
    def compute_signal(self, ctx):
        price = ctx.latest()
        if price > self.config.get('threshold', 100):
            return Signal.buy(confidence=0.7,
                reason=f'Price {price:.2f} above threshold')
        return Signal.hold()
```

## License

MIT - Zhou Yuchen
