"""Tests for the HTML research report generator."""

from __future__ import annotations

from kairos.reports.html_report import generate_html_report


def _report(**overrides) -> str:
    defaults = dict(
        token="AAPL",
        market_type="stock",
        strategy_name="momentum",
        decision="BUY",
        confidence=0.75,
        rationale="strong momentum",
        composite=70.0,
        rsi=55.0,
        signal="bullish",
        adx=25.0,
        atr=1.2,
        var_95=-0.03,
        cvar=-0.05,
        kelly=0.2,
        is_safe=True,
        price=150.0,
        n_bars=60,
    )
    defaults.update(overrides)
    return generate_html_report(**defaults)


class TestGenerateHtmlReport:
    def test_is_a_full_html_document(self):
        html = _report()
        assert html.startswith("<!DOCTYPE html>")
        assert html.rstrip().endswith("</html>")

    def test_contains_core_fields(self):
        html = _report()
        assert "AAPL" in html
        assert "BUY" in html
        assert "75%" in html  # confidence formatted as percent
        assert "momentum" in html

    def test_agent_traces_are_rendered(self):
        html = _report(
            agent_traces=[{"agent_name": "quant", "confidence": 0.6, "reasoning": "rsi low"}]
        )
        assert "Quant" in html
        assert "rsi low" in html

    def test_falls_back_when_no_agent_traces(self):
        assert "Research → Quant → Risk → Executor" in _report(agent_traces=None)

    def test_sell_decision_and_bearish_signal(self):
        html = _report(decision="SELL", signal="bearish")
        assert "SELL" in html
        assert "negative" in html  # bearish -> negative class

    def test_hold_decision_and_caution_status(self):
        html = _report(decision="HOLD", signal="neutral", is_safe=False)
        assert "HOLD" in html
        assert "Caution" in html

    def test_empty_signal_falls_back_to_placeholder(self):
        assert "?" in _report(signal="")
