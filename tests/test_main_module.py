"""Smoke test for the `python -m kairos` entry point."""

from __future__ import annotations


def test_main_module_exposes_app():
    import kairos.__main__ as main

    assert main.app is not None
