"""CLI application for Kairos."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
import rich.box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from kairos import __version__
from kairos.core.orchestrator import Orchestrator

app = typer.Typer(help="Kairos - AI Trading Agents, Fully Transparent & Verifiable")
console = Console()


@app.command()
def demo(
    token: str = typer.Option("SOL/USDT", "--token", "-t", help="Trading pair to analyze"),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for reproducibility"),
):
    asyncio.run(_run_demo(token, seed))


async def _run_demo(token: str, seed: int) -> None:
    console.print(Panel(f"[bold cyan]Kairos Demo[/bold cyan] - Analyzing {token}", style="cyan"))

    with console.status("[bold green]Running agent pipeline...") as status:
        orchestrator = Orchestrator()
        result = await orchestrator.run(token=token, mode="demo", seed=seed)

    decision = result["decision"]

    console.print("\n[bold]Final Decision:[/bold]")
    decision_value = decision.get("decision", "HOLD")
    if decision_value == "BUY":
        decision_color = "green"
    elif decision_value == "SELL":
        decision_color = "red"
    else:
        decision_color = "yellow"

    console.print(f"  [{decision_color} bold]{decision_value}[/{decision_color} bold]")
    console.print(f"  Confidence: {decision.get('confidence', 0.5):.2f}")

    if decision.get("size_usd"):
        console.print(f"  Position Size: ${decision['size_usd']:.2f}")
    if decision.get("is_risk_overridden"):
        console.print(f"  [red]Risk Override Active[/red]")

    console.print(f"\n  [dim]Rationale: {decision.get('decision_rationale', '')}[/dim]")

    console.print("\n[bold]Agent Pipeline:[/bold]")
    trace_table = Table(show_header=True, header_style="bold")
    trace_table.add_column("Agent", style="cyan")
    trace_table.add_column("Confidence", justify="right")
    trace_table.add_column("Output Summary", style="dim")

    for agent_result in result["trace"]:
        agent_name = agent_result.get("agent_name", "?")
        confidence = agent_result.get("confidence", 0)
        reasoning = agent_result.get("reasoning", "")[:60]
        trace_table.add_row(agent_name, f"{confidence:.2f}", reasoning)

    console.print(trace_table)

    console.print(f"\n[dim]Journal entries recorded: {result['journal_entries']}[/dim]")

    journal_dir = Path.home() / ".kairos"
    journal_path = journal_dir / "demo_journal.json"
    if journal_path.exists():
        console.print(f"[dim]Journal saved to: {journal_path}[/dim]")

    console.print("\n[bold green]Demo complete![/bold green]")


@app.command()
def dashboard(
    token: str = typer.Option("SOL/USDT", "--token", "-t", help="Trading pair to analyze"),
    mode: str = typer.Option("demo", "--mode", "-m", help="demo or live"),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed"),
):
    """Launch the Streamlit Dashboard for real-time agent visualization."""
    import subprocess
    import sys

    dashboard_path = Path(__file__).resolve().parent.parent / "dashboard" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(dashboard_path), "--"]
    cmd.extend(["--token", token, "--mode", mode, "--seed", str(seed)])
    subprocess.run(cmd)


def _is_stock_ticker(ticker: str) -> bool:
    """Detect if a ticker is likely a stock (not crypto format)."""
    up = ticker.upper()
    if "-USD" in up or "/" in up or up in ("BTC", "ETH", "SOL", "DOGE", "XRP"):
        return False
    if up in ("SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META",
              "GLD", "SLV", "TLT", "IWM", "VTI", "VOO", "BND", "DIA", "XLF", "XLK"):
        return True
    return len(ticker) <= 5 and ticker.isalpha()


@app.command()
def backtest(
    token: str = typer.Option("SOL/USDT", "--token", "-t", help="Trading pair / stock ticker"),
    strategy: str = typer.Option("momentum", "--strategy", "-s",
                                 help="Strategy name (momentum, mean_reversion, conservative)"),
    days: int = typer.Option(365, "--days", "-d", help="Days of data for backtest"),
    train_size: int = typer.Option(90, "--train", help="Training window size"),
    test_size: int = typer.Option(30, "--test", help="Test window size"),
    max_windows: int = typer.Option(None, "--max-windows", "-w", help="Max windows (faster for testing)"),
):
    """Run a walk-forward backtest with statistical validation.

    Examples:
        kairos backtest --strategy momentum --days 365
        kairos backtest --token AAPL --days 730
    """
    asyncio.run(_run_backtest(token, strategy, days, train_size, test_size, max_windows))


async def _run_backtest(token: str, strategy: str, days: int, train_size: int, test_size: int,
                         max_windows: int | None = None) -> None:
    from kairos.strategies.registry import StrategyRegistry
    from kairos.data.mock import MockDataProvider
    from kairos.backtesting.engine import WalkForwardEngine
    from kairos.statistics.bootstrap import BootstrapSignificanceTest

    registry = StrategyRegistry()
    try:
        cfg = registry.get(strategy)
    except KeyError:
        console.print(f"[red]Unknown strategy: {strategy}[/red]")
        console.print(f"Available: {registry.list()}")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold cyan]Backtest[/bold cyan] - {cfg.name}: {cfg.description}", style="cyan"))

    if _is_stock_ticker(token):
        with console.status(f"[bold green]Fetching {token} data via Yahoo Finance..."):
            from kairos.data.providers.yahoofinance import YahooFinanceProvider
            provider = YahooFinanceProvider()
            df = await provider.fetch_price_data(token, days=days)
        console.print(f"  [dim]Loaded {len(df)} rows for {token}[/dim]")
    else:
        df = MockDataProvider.generate_price_data(days=days // 30 + 1, seed=42)
    engine = WalkForwardEngine(df, train_size=train_size, test_size=test_size,
                                 max_windows=max_windows if max_windows else None)

    with console.status("[bold green]Running backtest...") as status:
        progress = {"current": 0, "total": 0}

        def on_progress(cur: int, tot: int):
            progress["current"] = cur
            progress["total"] = tot
            status.update(f"[bold green]Processing window {cur}/{tot}...")

        result = engine.run(cfg.agent_config, progress_callback=on_progress)
        n_windows = result.get("n_windows", 0)
        status.update(f"[bold green]Backtest complete — {n_windows} windows analyzed")

        if result["all_returns"]:
            bst = BootstrapSignificanceTest(result["all_returns"], n_iterations=500, seed=42)
            sig = bst.run()
        else:
            sig = {"sharpe_observed": 0, "p_value": 1.0,
                   "is_significant": False, "sharpe_ci_95": (0, 0)}

    agg = result["aggregate"]
    bench = result.get("benchmark", {})

    console.print("\n[bold]Performance vs Benchmark:[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Strategy", justify="right")
    table.add_column("Benchmark", justify="right")
    table.add_column("Δ", justify="right")

    strat_ret = f"{agg['cumulative_return']:.2%}"
    bench_ret = f"{bench.get('cumulative_return', 0):.2%}"
    ret_diff = agg['cumulative_return'] - bench.get('cumulative_return', 0)
    diff_str = f"{ret_diff:+.2%}" if ret_diff != 0 else "—"
    table.add_row("Cumulative Return", strat_ret, bench_ret, diff_str)

    strat_sharpe = f"{agg['sharpe_ratio']:.2f}"
    bench_sharpe = f"{bench.get('sharpe_ratio', 0):.2f}"
    table.add_row("Sharpe Ratio", strat_sharpe, bench_sharpe, "—")

    table.add_row("Max Drawdown", f"{agg['max_drawdown']:.2%}", f"{bench.get('max_drawdown', 0):.2%}", "—")
    table.add_row("Win Rate", f"{agg['win_rate']:.2%}", f"{bench.get('win_rate', 0):.2%}", "—")
    table.add_row("Profit Factor", f"{agg['profit_factor'] or 'N/A'}", "—", "—")
    table.add_row("Windows", str(result["n_windows"]), "—", "—")
    console.print(table)

    console.print("\n[bold]Statistical Significance:[/bold]")
    sig_color = "green" if sig["is_significant"] else "yellow"
    console.print(f"  Sharpe (observed): [bold]{sig['sharpe_observed']:.3f}[/bold]")
    console.print(f"  95% CI: ({sig['sharpe_ci_95'][0]:.3f}, {sig['sharpe_ci_95'][1]:.3f})")
    console.print(f"  p-value: {sig['p_value']:.4f}")
    console.print(f"  Significant: [{sig_color}]{sig['is_significant']}[/{sig_color}]")

    console.print("\n[bold green]Backtest complete![/bold green]")


@app.command()
def analyze(
    token: str = typer.Argument(..., help="Stock ticker (AAPL) or crypto pair (BTC-USD)"),
    strategy: str = typer.Option("momentum", "--strategy", "-s",
                                  help="Strategy name (momentum, mean_reversion, conservative)"),
    days: int = typer.Option(365, "--days", "-d", help="Days of historical data"),
):
    """Analyze a stock or crypto asset using the full AI agent pipeline.

    Fetches real market data via Yahoo Finance, runs the 4-agent pipeline
    (Research → Quant → Risk → Executor), and shows the full analysis.

    Examples:
        kairos analyze AAPL
        kairos analyze BTC-USD --days 90
        kairos analyze SPY --strategy conservative
    """
    asyncio.run(_run_analyze(token, strategy, days))


def _sparkline(data: list[float], width: int = 40) -> str:
    """Generate a Unicode sparkline from numeric data."""
    if not data:
        return ""
    bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    arr = list(data)
    mn, mx = min(arr), max(arr)
    if mx == mn:
        return bars[3] * min(width, len(arr))
    step = max(1, len(arr) // width)
    sampled = arr[::step][:width]
    indices = [int((v - mn) / (mx - mn) * (len(bars) - 1)) for v in sampled]
    return "".join(bars[i] for i in indices)


async def _run_analyze(token: str, strategy: str, days: int) -> None:
    from kairos.strategies.registry import StrategyRegistry
    from kairos.data.providers.yahoofinance import YahooFinanceProvider
    from kairos.agents.quant import QuantAgent
    from kairos.agents.risk import RiskAgent
    from kairos.agents.executor import ExecutorAgent
    from kairos.agents.base import AgentContext
    from kairos.core.journal import DecisionJournal

    registry = StrategyRegistry()
    try:
        cfg = registry.get(strategy)
    except KeyError:
        console.print(f"[red]Unknown strategy: {strategy}[/red]")
        console.print(f"Available: {registry.list()}")
        raise typer.Exit(code=1)

    market_type = "stock" if _is_stock_ticker(token) else "crypto"
    console.print(Panel(f"[bold cyan]Kairos Analyze[/bold cyan] — {token} ({market_type})  |  Strategy: {cfg.name}",
                        style="cyan"))

    with console.status("[bold green]Fetching market data..."):
        provider = YahooFinanceProvider()
        df = await provider.fetch_price_data(token, days=days)

    with console.status("[bold green]Running agent pipeline..."):
        journal = DecisionJournal()
        quant = QuantAgent(cfg.agent_config)
        qctx = AgentContext(input_data={"ohlcv": df, "token": token})
        quant_result = await quant.process(qctx)

        risk = RiskAgent(cfg.agent_config)
        rctx2 = AgentContext(input_data={"portfolio_value": 10000, "token": token})
        risk_result = await risk.process(rctx2)

        executor = ExecutorAgent(cfg.agent_config, journal=journal)
        ectx = AgentContext(input_data={
            "quant_output": quant_result.output,
            "risk_output": risk_result.output,
            "token": token, "mode": "live",
            "current_price": float(df["close"].iloc[-1]) if not df.empty else 100,
        })
        executor_result = await executor.process(ectx)

    # ── Decision Banner ───────────────────────────────────────────────────
    d = executor_result.output.get("decision", "HOLD")
    d_color = "green" if d == "BUY" else ("red" if d == "SELL" else "yellow")
    confidence = executor_result.output.get("confidence", 0.5)
    rationale = executor_result.output.get("decision_rationale", "")

    decision_panel = Panel.fit(
        f"[bold {d_color}]{d}[/bold {d_color}]  (confidence: {confidence:.0%})\n"
        f"[dim]{rationale}[/dim]",
        title="Decision",
        border_style=d_color,
    )
    console.print(decision_panel)

    # ── Price + Indicators side by side ──────────────────────────────────
    closes = df["close"].tolist()
    spark = _sparkline(closes, width=50)

    qo = quant_result.output
    indicator_table = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    indicator_table.add_column("Indicator", style="cyan", width=16)
    indicator_table.add_column("Value", justify="right", width=10)
    indicator_table.add_row("Composite Score", f"{qo.get('composite_score', 0):.0f}/100")
    indicator_table.add_row("RSI(14)", f"{qo.get('rsi_14', 0):.1f}")
    indicator_table.add_row("Signal", f"[bold]{qo.get('signal', '?').upper()}[/bold]")
    indicator_table.add_row("ADX", f"{qo.get('adx_14', 0):.1f}")
    indicator_table.add_row("ATR", f"{qo.get('atr_14', 0):.2f}")

    price = closes[-1] if closes else 0
    change = ((closes[-1] - closes[0]) / closes[0] * 100) if len(closes) >= 2 else 0
    price_panel = Panel.fit(
        f"[bold]${price:.2f}[/bold]\n"
        f"[{'green' if change >= 0 else 'red'}]{change:+.2f}%[/] over {len(closes)} bars\n\n"
        f"{spark}",
        title=f"{token} Price Trend",
        border_style="blue",
    )

    col = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    col.add_column("Left")
    col.add_column("Right")
    col.add_row(price_panel, indicator_table)
    console.print(col)

    # ── Risk + Stats ─────────────────────────────────────────────────────
    ro = risk_result.output
    risk_table = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    risk_table.add_column("Metric", style="cyan", width=16)
    risk_table.add_column("Value", justify="right", width=10)
    risk_table.add_row("VaR(95%)", f"{ro.get('var_95', 0):.2%}")
    risk_table.add_row("CVaR(95%)", f"{ro.get('cvar_95', 0):.2%}")
    risk_table.add_row("VaR(99%)", f"{ro.get('var_99', 0):.2%}")
    risk_table.add_row("Kelly Fraction", f"{ro.get('kelly_fraction', 0):.2f}")
    safe = ro.get("is_safe", True)
    risk_table.add_row("Status", "[green]Safe[/green]" if safe else "[yellow]Caution[/yellow]")

    stats_table = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan", width=16)
    stats_table.add_column("Value", justify="right", width=10)
    stats_table.add_row("Data Points", str(len(df)))
    stats_table.add_row("Date Range", f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
    stats_table.add_row("Strategy", cfg.name)
    stats_table.add_row("Market", market_type.title())

    col2 = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    col2.add_column("Left")
    col2.add_column("Right")
    col2.add_row(risk_table, stats_table)
    console.print(col2)

    console.print(f"\n[dim]Journal entries: {len(journal.get_all())}  |  "
                  f"kairos report {token} for detailed report[/dim]")
    console.print(f"\n[bold green]Analysis complete![/bold green]")


@app.command()
def report(
    token: str = typer.Argument(..., help="Stock ticker or crypto pair"),
    strategy: str = typer.Option("momentum", "--strategy", "-s",
                                  help="Strategy name"),
    days: int = typer.Option(365, "--days", "-d", help="Days of historical data"),
    output: str = typer.Option("kairos_report.html", "--output", "-o", help="Output HTML file"),
):
    """Generate a beautiful HTML research report for any asset.

    Creates a self-contained HTML report with decision, technical signals,
    risk assessment, and agent reasoning — shareable and printable.

    Examples:
        kairos report AAPL
        kairos report BTC-USD --days 90 -o btc_report.html
    """
    asyncio.run(_run_report(token, strategy, days, output))


async def _run_report(token: str, strategy: str, days: int, output: str) -> None:
    from kairos.strategies.registry import StrategyRegistry
    from kairos.data.providers.yahoofinance import YahooFinanceProvider
    from kairos.agents.quant import QuantAgent
    from kairos.agents.risk import RiskAgent
    from kairos.agents.executor import ExecutorAgent
    from kairos.agents.base import AgentContext
    from kairos.reports.html_report import generate_html_report

    registry = StrategyRegistry()
    cfg = registry.get(strategy)
    market_type = "stock" if _is_stock_ticker(token) else "crypto"

    with console.status(f"[bold green]Analyzing {token}..."):
        provider = YahooFinanceProvider()
        df = await provider.fetch_price_data(token, days=days)

        quant = QuantAgent(cfg.agent_config)
        qr = await quant.process(AgentContext(input_data={"ohlcv": df}))
        qo = qr.output

        risk = RiskAgent(cfg.agent_config)
        rr = await risk.process(AgentContext(input_data={"portfolio_value": 10000}))
        ro = rr.output

        executor = ExecutorAgent(cfg.agent_config)
        er = await executor.process(AgentContext(input_data={
            "quant_output": qo, "risk_output": ro,
            "token": token, "mode": "live",
            "current_price": float(df["close"].iloc[-1]) if not df.empty else 100,
        }))

    d = er.output
    html = generate_html_report(
        token=token, market_type=market_type, strategy_name=cfg.name,
        decision=d.get("decision", "HOLD"),
        confidence=d.get("confidence", 0.5),
        rationale=d.get("decision_rationale", ""),
        composite=qo.get("composite_score", 0),
        rsi=qo.get("rsi_14", 0),
        signal=qo.get("signal", ""),
        adx=qo.get("adx_14", 0),
        atr=qo.get("atr_14", 0),
        var_95=ro.get("var_95", 0),
        cvar=ro.get("cvar_95", 0),
        kelly=ro.get("kelly_fraction", 0),
        is_safe=ro.get("is_safe", True),
        price=float(df["close"].iloc[-1]) if not df.empty else 0,
        n_bars=len(df),
        agent_traces=[qr.model_dump(), rr.model_dump(), er.model_dump()],
    )

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    console.print(f"[green]Report saved to[/green] {output}")
    console.print(f"[dim]Open in your browser to view the analysis.[/dim]")


@app.command()
def compare(
    token: str = typer.Argument(..., help="Stock ticker or crypto pair"),
    strategies: str = typer.Option("momentum,mean_reversion", "--strategies",
                                    help="Comma-separated strategy names"),
    days: int = typer.Option(365, "--days", "-d", help="Days of data"),
):
    """Compare multiple strategies side-by-side for any asset.

    Examples:
        kairos compare AAPL
        kairos compare BTC-USD --strategies momentum,conservative --days 90
    """
    asyncio.run(_run_compare(token, strategies.split(","), days))


async def _run_compare(token: str, strategy_names: list[str], days: int) -> None:
    from kairos.strategies.registry import StrategyRegistry
    from kairos.data.providers.yahoofinance import YahooFinanceProvider
    from kairos.backtesting.engine import WalkForwardEngine
    from kairos.statistics.bootstrap import BootstrapSignificanceTest

    registry = StrategyRegistry()
    configs = []
    for name in strategy_names:
        try:
            configs.append(registry.get(name))
        except KeyError:
            console.print(f"[red]Unknown strategy: {name}[/red]")
            raise typer.Exit(code=1)

    market_type = "stock" if _is_stock_ticker(token) else "crypto"
    console.print(Panel(f"[bold cyan]Strategy Comparison[/bold cyan] — {token} ({market_type})",
                        style="cyan"))

    with console.status(f"[bold green]Fetching {token} data..."):
        provider = YahooFinanceProvider()
        df = await provider.fetch_price_data(token, days=days)

    console.print("\n[bold]Results:[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Strategy", style="cyan")
    table.add_column("Return", justify="right")
    table.add_column("Sharpe", justify="right")
    table.add_column("Max DD", justify="right")
    table.add_column("Win Rate", justify="right")
    table.add_column("p-value", justify="right")

    for cfg in configs:
        engine = WalkForwardEngine(df, train_size=min(90, len(df) // 3),
                                    test_size=min(30, len(df) // 6))
        result = engine.run(cfg.agent_config)
        agg = result["aggregate"]
        sig = {"p_value": 1.0}
        if result["all_returns"]:
            bst = BootstrapSignificanceTest(result["all_returns"], n_iterations=200, seed=42)
            sig = bst.run()

        sig_text = f"{sig['p_value']:.3f}" if sig["p_value"] < 0.1 else f"{sig['p_value']:.2f}"
        if sig.get("is_significant"):
            sig_text += "*"

        table.add_row(
            cfg.name,
            f"{agg['cumulative_return']:.1%}",
            f"{agg['sharpe_ratio']:.2f}",
            f"{agg['max_drawdown']:.1%}",
            f"{agg['win_rate']:.0%}",
            sig_text,
        )

    console.print(table)
    console.print("\n[dim]* p < 0.05 = statistically significant[/dim]")
    console.print("[bold green]Comparison complete![/bold green]")


@app.command()
def leaderboard(
    token: str = typer.Argument(..., help="Stock ticker or crypto pair"),
    days: int = typer.Option(365, "--days", "-d", help="Days of historical data"),
):
    """Rank all built-in strategies by performance for any asset.

    Runs every strategy through walk-forward backtesting and ranks them
    by Sharpe ratio, return, and statistical significance.

    Examples:
        kairos leaderboard AAPL
        kairos leaderboard BTC-USD --days 180
    """
    asyncio.run(_run_leaderboard(token, days))


async def _run_leaderboard(token: str, days: int) -> None:
    from kairos.strategies.registry import StrategyRegistry
    from kairos.strategies.builtin import BUILTIN_STRATEGIES
    from kairos.data.providers.yahoofinance import YahooFinanceProvider
    from kairos.backtesting.engine import WalkForwardEngine
    from kairos.statistics.bootstrap import BootstrapSignificanceTest

    market_type = "stock" if token.upper().isalpha() and len(token) <= 5 else "crypto"
    console.print(Panel(f"[bold cyan]Strategy Leaderboard[/bold cyan] — {token} ({market_type})",
                        style="cyan"))

    with console.status(f"[bold green]Fetching {token} data..."):
        provider = YahooFinanceProvider()
        df = await provider.fetch_price_data(token, days=days)

    results = []
    with console.status("[bold green]Running all strategies...") as status:
        for i, (name, strategy_cls) in enumerate(BUILTIN_STRATEGIES.items()):
            status.update(f"[bold green]Testing {name} ({i+1}/{len(BUILTIN_STRATEGIES)})")
            engine = WalkForwardEngine(df, train_size=min(90, len(df) // 3),
                                        test_size=min(30, len(df) // 6))
            result = engine.run({"name": name})
            agg = result["aggregate"]
            sig = {"p_value": 1.0, "is_significant": False}
            if result["all_returns"]:
                bst = BootstrapSignificanceTest(result["all_returns"], n_iterations=200, seed=42)
                sig = bst.run()
            results.append((name, agg, sig))

    results.sort(key=lambda x: x[1]["sharpe_ratio"], reverse=True)

    table = Table(show_header=True, header_style="bold", title=f"Ranked by Sharpe Ratio")
    table.add_column("Rank", justify="right", style="dim", width=5)
    table.add_column("Strategy", style="cyan")
    table.add_column("Return", justify="right")
    table.add_column("Sharpe", justify="right")
    table.add_column("Max DD", justify="right")
    table.add_column("Win Rate", justify="right")
    table.add_column("p-value", justify="right")

    for rank, (name, agg, sig) in enumerate(results, 1):
        medal = {1: "#1 ", 2: "#2 ", 3: "#3 "}.get(rank, "")
        sig_text = f"{sig['p_value']:.3f}" if sig['p_value'] < 0.1 else f"{sig['p_value']:.2f}"
        if sig.get("is_significant"):
            sig_text += "*"
        table.add_row(
            f"{rank}",
            f"{medal}{name}",
            f"{agg['cumulative_return']:.1%}",
            f"{agg['sharpe_ratio']:.2f}",
            f"{agg['max_drawdown']:.1%}",
            f"{agg['win_rate']:.0%}",
            sig_text,
        )

    console.print(table)
    console.print("\n[dim]* p < 0.05 = statistically significant[/dim]")
    console.print("[bold green]Leaderboard complete![/bold green]")


@app.command()
def paper(
    symbol: str = typer.Argument(..., help="Stock symbol to trade"),
    strategy: str = typer.Option("momentum", "--strategy", "-s", help="Strategy name"),
    days: int = typer.Option(90, "--days", "-d", help="Days of historical data for signal"),
    qty: float = typer.Option(1.0, "--qty", "-q", help="Number of shares to trade"),
):
    """Paper trade using Alpaca's free paper trading API.

    Requires ALPACA_API_KEY_ID and ALPACA_SECRET_KEY environment variables.
    Get yours free at https://alpaca.markets

    Analyzes the asset with the full AI pipeline, then places a paper trade
    if the signal is BUY or SELL.

    Examples:
        kairos paper AAPL
        kairos paper MSFT --strategy conservative --qty 10
    """
    asyncio.run(_run_paper(symbol, strategy, days, qty))


async def _run_paper(symbol: str, strategy: str, days: int, qty: float) -> None:
    from kairos.brokers.alpaca import AlpacaBroker
    from kairos.strategies.registry import StrategyRegistry
    from kairos.data.providers.yahoofinance import YahooFinanceProvider
    from kairos.agents.quant import QuantAgent
    from kairos.agents.risk import RiskAgent
    from kairos.agents.executor import ExecutorAgent
    from kairos.agents.base import AgentContext

    broker = AlpacaBroker()
    if not broker.is_connected:
        console.print("[red]Alpaca not configured.[/red]")
        console.print("Set [bold]ALPACA_API_KEY_ID[/bold] and [bold]ALPACA_SECRET_KEY[/bold]")
        console.print("Get yours free at https://alpaca.markets")
        raise typer.Exit(code=1)

    registry = StrategyRegistry()
    cfg = registry.get(strategy)
    mode = "paper"
    console.print(Panel(f"[bold cyan]Paper Trade[/bold cyan] — {symbol} | Strategy: {cfg.name} | Qty: {qty}",
                        style="cyan"))

    # Fetch data and run analysis
    with console.status("[bold green]Analyzing market..."):
        provider = YahooFinanceProvider()
        df = await provider.fetch_price_data(symbol, days=days)
        quant = QuantAgent(cfg.agent_config)
        qr = await quant.process(AgentContext(input_data={"ohlcv": df}))
        risk = RiskAgent(cfg.agent_config)
        rr = await risk.process(AgentContext(input_data={"portfolio_value": 10000}))
        executor = ExecutorAgent(cfg.agent_config)
        er = await executor.process(AgentContext(input_data={
            "quant_output": qr.output, "risk_output": rr.output,
            "token": symbol, "mode": "live",
            "current_price": float(df["close"].iloc[-1]) if not df.empty else 100,
        }))

    decision = er.output.get("decision", "HOLD")
    price = float(df["close"].iloc[-1]) if not df.empty else 0
    console.print(f"\n[bold]Signal:[/bold] {decision} at ~${price:.2f}")

    if decision in ("BUY", "SELL"):
        with console.status(f"[bold green]Placing {decision.lower()} order..."):
            side = "buy" if decision == "BUY" else "sell"
            order = await broker.place_order(symbol, side, qty)
            await broker.close()
        if order.status == "filled":
            console.print(f"[green]Order filled![/green] {order.side} {order.filled_qty} {symbol} "
                          f"at ${order.filled_avg_price:.2f}")
        elif order.status == "accepted":
            console.print(f"[yellow]Order accepted, pending fill.[/yellow] ID: {order.id}")
        else:
            console.print(f"[yellow]Order status: {order.status}[/yellow]")
    else:
        console.print("[dim]No trade signal. Try a different strategy or asset.[/dim]")
    console.print("[bold green]Paper trade analysis complete![/bold green]")


@app.command()
def live(
    symbol: str = typer.Argument(..., help="Stock symbol"),
    strategy: str = typer.Option("momentum", "--strategy", "-s", help="Strategy"),
    qty: float = typer.Option(1.0, "--qty", "-q", help="Shares to trade"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Live trade with REAL MONEY via Alpaca.

    Requires ALPACA_API_KEY_ID, ALPACA_SECRET_KEY, and ALPACA_LIVE=true.

    WARNING: This places real trades. Start with paper trading first.
    """
    asyncio.run(_run_live(symbol, strategy, qty, confirm))


async def _run_live(symbol: str, strategy: str, qty: float, confirm: bool) -> None:
    from kairos.brokers.alpaca import AlpacaBroker

    if not confirm:
        console.print("[bold red]WARNING: This will trade with REAL MONEY![/bold red]")
        console.print("Pass --yes to confirm, or use 'kairos paper' for paper trading.")
        raise typer.Exit(code=1)

    broker = AlpacaBroker(live=True)
    if not broker.is_connected:
        console.print("[red]Alpaca live trading not configured.[/red]")
        console.print("Set ALPACA_API_KEY_ID, ALPACA_SECRET_KEY, and ALPACA_LIVE=true")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold red]LIVE TRADE[/bold red] — {symbol} x {qty} | Strategy: {strategy}",
                        style="red"))
    console.print("[bold red]This is a REAL trade with REAL money![/bold red]")

    from kairos.strategies.registry import StrategyRegistry
    from kairos.data.providers.yahoofinance import YahooFinanceProvider
    from kairos.agents.quant import QuantAgent
    from kairos.agents.risk import RiskAgent
    from kairos.agents.executor import ExecutorAgent
    from kairos.agents.base import AgentContext

    registry = StrategyRegistry()
    cfg = registry.get(strategy)

    with console.status("[bold green]Analyzing..."):
        provider = YahooFinanceProvider()
        df = await provider.fetch_price_data(symbol, days=90)
        quant = QuantAgent(cfg.agent_config)
        qr = await quant.process(AgentContext(input_data={"ohlcv": df}))
        risk = RiskAgent(cfg.agent_config)
        rr = await risk.process(AgentContext(input_data={"portfolio_value": 10000}))
        executor = ExecutorAgent(cfg.agent_config)
        er = await executor.process(AgentContext(input_data={
            "quant_output": qr.output, "risk_output": rr.output,
            "token": symbol, "mode": "live",
            "current_price": float(df["close"].iloc[-1]) if not df.empty else 100,
        }))

    decision = er.output.get("decision", "HOLD")
    if decision in ("BUY", "SELL"):
        side = "buy" if decision == "BUY" else "sell"
        order = await broker.place_order(symbol, side, qty)
        await broker.close()
        if order.status == "filled":
            console.print(f"[green]LIVE order filled![/green] {side.upper()} {qty} {symbol}")
        else:
            console.print(f"[yellow]Order status: {order.status}[/yellow]")
    else:
        console.print("[dim]No trade signal generated.[/dim]")
    console.print("[bold red]Live trade complete. Monitor your account![/bold red]")


@app.command()
def broker_status():
    """Check Alpaca broker connection and account status."""
    asyncio.run(_run_broker_status())


async def _run_broker_status():
    from kairos.brokers.alpaca import AlpacaBroker
    broker = AlpacaBroker()
    if not broker.is_connected:
        console.print("[red]Alpaca not configured.[/red]")
        console.print("Set ALPACA_API_KEY_ID and ALPACA_SECRET_KEY environment variables.")
        raise typer.Exit(code=1)
    try:
        account = await broker.get_account()
        positions = await broker.get_positions()
        await broker.close()
        console.print(Panel(f"[bold cyan]Alpaca Broker Status[/bold cyan]", style="cyan"))
        console.print(f"  Account: [green]{account['status']}[/green]")
        console.print(f"  Equity: ${account['equity']:,.2f}")
        console.print(f"  Cash: ${account['cash']:,.2f}")
        console.print(f"  Buying Power: ${account['buying_power']:,.2f}")
        console.print(f"  Positions: {len(positions)}")
        for p in positions:
            pl = p.get("unrealized_pl", 0)
            pl_str = f"[green]+${pl:.2f}[/green]" if pl >= 0 else f"[red]-${abs(pl):.2f}[/red]"
            console.print(f"    {p['symbol']}: {p['qty']} shares @ ${p['current_price']:.2f} ({pl_str})")
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version and exit."""
    rprint(f"Kairos v{__version__}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit"),
):
    if version:
        rprint(f"Kairos v{__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        rprint(f"Kairos v{__version__}")
        rprint("")
        rprint("Usage: kairos [COMMAND] [ARGS]...")
        rprint("")
        rprint("Commands:")
        rprint("  analyze    Analyze a stock/crypto with the full AI agent pipeline")
        rprint("  backtest   Walk-forward backtesting with benchmark comparison")
        rprint("  broker-status  Check Alpaca broker connection and account")
        rprint("  compare    Compare multiple strategies side-by-side")
        rprint("  dashboard  Launch interactive Streamlit Dashboard")
        rprint("  demo       Run a full demo with mock data (no API keys)")
        rprint("  leaderboard  Rank all strategies by performance")
        rprint("  live       LIVE trade with real money (requires confirmation)")
        rprint("  paper      Paper trade via Alpaca (free, requires API key)")
        rprint("  report     Generate a beautiful HTML research report")
        rprint("  version    Show version and exit")
        rprint("")
        rprint("")
        rprint("Examples:")
        rprint("  kairos analyze AAPL")
        rprint("  kairos leaderboard AAPL")
        rprint("  kairos paper AAPL --qty 10")
        rprint("  kairos report AAPL -o report.html")
        rprint("  kairos backtest --token AAPL --days 730")
        rprint("")
        rprint("Run 'kairos COMMAND --help' for more details.")