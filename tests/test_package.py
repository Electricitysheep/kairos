"""Tests for the top-level ``kairos`` package surface."""

from __future__ import annotations

import kairos


def test_version_is_exposed():
    assert isinstance(kairos.__version__, str)
    assert kairos.__version__


def test_lazy_exports_resolve():
    assert kairos.Orchestrator.__name__ == "Orchestrator"
    assert kairos.Signal.__name__ == "Signal"
    assert kairos.Strategy.__name__ == "Strategy"
    assert kairos.StrategyContext.__name__ == "StrategyContext"


def test_unknown_attribute_raises():
    try:
        kairos.DoesNotExist  # noqa: B018
    except AttributeError as exc:
        assert "DoesNotExist" in str(exc)
    else:
        raise AssertionError("expected AttributeError for unknown attribute")


def test_dir_lists_public_api():
    names = dir(kairos)
    assert "Orchestrator" in names
    assert "Signal" in names
