"""Tests for the Kairos CLI."""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from kairos import __version__
from kairos.cli.app import app
from kairos.data.mock import MockDataProvider

runner = CliRunner()

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _plain(result) -> str:
    """Strip ANSI color codes so option flags match as plain substrings.

    Rich/Typer inserts SGR escape codes between the dashes of an option
    (e.g. ``--token`` renders as ``-\x1b[0m\x1b[1;36m-token``), which varies
    by Rich version and breaks naive substring checks.
    """
    return _ANSI.sub("", result.stdout)


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"Kairos v{__version__}" in result.stdout


def test_demo_help():
    result = runner.invoke(app, ["demo", "--help"])
    assert result.exit_code == 0
    out = _plain(result)
    assert "--token" in out or "-t" in out
    assert "--seed" in out or "-s" in out


def test_demo_runs_successfully():
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "Decision" in result.stdout or "Final Decision" in result.stdout
    decision_line = result.stdout
    assert any(d in decision_line for d in ["BUY", "SELL", "HOLD"])


def test_dashboard_help():
    result = runner.invoke(app, ["dashboard", "--help"])
    assert result.exit_code == 0
    out = _plain(result)
    assert "--token" in out
    assert "--mode" in out


def test_no_args_shows_usage():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Kairos" in result.stdout


def test_backtest_help():
    result = runner.invoke(app, ["backtest", "--help"])
    assert result.exit_code == 0
    assert "--strategy" in _plain(result)


def test_backtest_unknown_strategy():
    result = runner.invoke(app, ["backtest", "--strategy", "nonexistent"])
    assert result.exit_code != 0


def test_analyze_help_lists_webhook():
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "--webhook" in _plain(result)


def test_analyze_webhook_pushes_decision():
    """--webhook should deliver the decision as a TradeAlert."""
    df = MockDataProvider.generate_price_data(days=60, seed=1)
    fake_provider = MagicMock()
    fake_provider.fetch_price_data = AsyncMock(return_value=df)

    sent = []

    class _FakeNotifier:
        def __init__(self, url):
            self.url = url

        async def send(self, alert):
            sent.append((self.url, alert))
            return True

    with (
        patch(
            "kairos.data.providers.yahoofinance.YahooFinanceProvider",
            return_value=fake_provider,
        ),
        patch("kairos.notifications.WebhookNotifier", _FakeNotifier),
    ):
        result = runner.invoke(app, ["analyze", "AAPL", "--webhook", "https://hook.test/x"])

    assert result.exit_code == 0, result.stdout
    assert len(sent) == 1
    url, alert = sent[0]
    assert url == "https://hook.test/x"
    assert alert.token == "AAPL"
    assert alert.decision in {"BUY", "SELL", "HOLD"}


def _patch_yahoo(days: int = 150):
    """Patch YahooFinanceProvider so CLI commands run offline on mock data."""
    df = MockDataProvider.generate_price_data(days=days, seed=1)
    fake = MagicMock()
    fake.fetch_price_data = AsyncMock(return_value=df)
    return patch(
        "kairos.data.providers.yahoofinance.YahooFinanceProvider",
        return_value=fake,
    )


def test_backtest_runs_on_mock_data():
    with _patch_yahoo():
        result = runner.invoke(app, ["backtest", "--token", "AAPL", "--max-windows", "2"])
    assert result.exit_code == 0, result.stdout


def test_report_writes_html_file(tmp_path):
    out = tmp_path / "report.html"
    with _patch_yahoo():
        result = runner.invoke(app, ["report", "AAPL", "-o", str(out)])
    assert result.exit_code == 0, result.stdout
    assert out.exists()
    assert "<!DOCTYPE html>" in out.read_text(encoding="utf-8")


def test_compare_runs():
    with _patch_yahoo():
        result = runner.invoke(
            app, ["compare", "AAPL", "--strategies", "momentum,rsi", "--days", "150"]
        )
    assert result.exit_code == 0, result.stdout


def test_compare_unknown_strategy_exits():
    with _patch_yahoo():
        result = runner.invoke(app, ["compare", "AAPL", "--strategies", "nope"])
    assert result.exit_code != 0


def test_leaderboard_runs():
    with _patch_yahoo():
        result = runner.invoke(app, ["leaderboard", "AAPL", "--days", "150"])
    assert result.exit_code == 0, result.stdout


def test_dashboard_launches_streamlit():
    with patch("subprocess.run") as mock_run:
        result = runner.invoke(app, ["dashboard"])
    assert result.exit_code == 0
    mock_run.assert_called_once()


def test_paper_without_credentials_is_handled():
    # No ALPACA_* env vars in CI → broker is not connected; must not crash.
    with _patch_yahoo():
        result = runner.invoke(app, ["paper", "AAPL"])
    assert result.exit_code in (0, 1)
    assert result.exception is None or isinstance(result.exception, SystemExit)


def test_broker_status_runs():
    result = runner.invoke(app, ["broker-status"])
    assert result.exit_code in (0, 1)
    assert result.exception is None or isinstance(result.exception, SystemExit)
