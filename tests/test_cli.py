"""Tests for the Kairos CLI."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from kairos.cli.app import app
from kairos import __version__


runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"Kairos v{__version__}" in result.stdout


def test_demo_help():
    result = runner.invoke(app, ["demo", "--help"])
    assert result.exit_code == 0
    assert "--token" in result.stdout or "-t" in result.stdout
    assert "--seed" in result.stdout or "-s" in result.stdout


def test_demo_runs_successfully():
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "Decision" in result.stdout or "Final Decision" in result.stdout
    decision_line = result.stdout
    assert any(d in decision_line for d in ["BUY", "SELL", "HOLD"])


def test_dashboard_help():
    result = runner.invoke(app, ["dashboard", "--help"])
    assert result.exit_code == 0
    assert "--token" in result.stdout
    assert "--mode" in result.stdout


def test_no_args_shows_usage():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Kairos" in result.stdout


def test_backtest_help():
    result = runner.invoke(app, ["backtest", "--help"])
    assert result.exit_code == 0
    assert "--strategy" in result.stdout


def test_backtest_unknown_strategy():
    result = runner.invoke(app, ["backtest", "--strategy", "nonexistent"])
    assert result.exit_code != 0