"""Tests for the Kairos CLI."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from kairos import __version__
from kairos.cli.app import app

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
