"""Kairos Dashboard — real-time AI agent pipeline visualization."""

from __future__ import annotations

import asyncio
from pathlib import Path

import streamlit as st
import pandas as pd

from kairos.core.orchestrator import Orchestrator

# ── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Kairos — AI Agent Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for professional quant aesthetic ──────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 1.5rem;
    }
    .decision-banner {
        padding: 1.2rem 1.5rem;
        border-radius: 0.6rem;
        margin-bottom: 1.2rem;
        border-left: 6px solid;
        background: #1a1a2e;
    }
    .decision-banner h1 {
        margin: 0;
        font-size: 1.8rem;
    }
    .decision-banner .meta {
        margin-top: 0.4rem;
        font-size: 0.9rem;
        color: #aaa;
    }
    .metric-card {
        background: #16213e;
        border-radius: 0.5rem;
        padding: 0.8rem 1rem;
        border: 1px solid #1e3a5f;
    }
    .metric-card .label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #888;
    }
    .metric-card .value {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 0.2rem;
    }
    .agent-card {
        background: #0f3460;
        border-radius: 0.5rem;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }
    .agent-card .agent-name {
        font-weight: 600;
        font-size: 0.9rem;
    }
    .agent-card .agent-conf {
        font-size: 0.8rem;
        color: #aaa;
    }
    .agent-card .agent-reasoning {
        font-size: 0.85rem;
        color: #ccc;
        margin-top: 0.3rem;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)


def run() -> None:
    st.markdown('<div class="main-header">Kairos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI Trading Agents &middot; Fully Transparent &amp; Verifiable</div>',
                unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    token = st.sidebar.text_input("Asset", value="SOL/USDT", key="token",
                                  help="Stock ticker (AAPL), crypto (BTC-USD), or mock")
    mode = st.sidebar.selectbox("Mode", ["demo", "live"], index=0, key="mode",
                                help="demo = mock data, live = real API data")
    seed = st.sidebar.number_input("Seed", value=42, min_value=0, key="seed")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        run_btn = st.button("Run Analysis", type="primary")
    with col2:
        clear_btn = st.button("Clear")

    if clear_btn:
        for key in ["last_result", "pipeline_error"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    if run_btn:
        _run_analysis(token, mode, int(seed))

    # ── Show pipeline error if any ────────────────────────────────────────────
    if "pipeline_error" in st.session_state:
        st.error(st.session_state.pipeline_error)
        if st.button("Dismiss"):
            del st.session_state.pipeline_error
            st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    if "last_result" in st.session_state:
        _display_results(st.session_state.last_result)
    else:
        st.info("Enter an asset and click **Run Analysis** to start the agent pipeline.", icon="ℹ️")


def _run_analysis(token: str, mode: str, seed: int) -> None:
    if not token or not token.strip():
        st.error("Asset name cannot be empty.")
        return
    if seed < 0:
        st.error("Seed must be non-negative.")
        return

    try:
        with st.spinner("Running agent pipeline..."):
            orchestrator = Orchestrator()
            result = asyncio.run(orchestrator.run(token=token, mode=mode, seed=seed))
        st.session_state.last_result = result
        if "pipeline_error" in st.session_state:
            del st.session_state.pipeline_error
        st.rerun()
    except ValueError as e:
        st.session_state.pipeline_error = f"Invalid input: {e}"
        st.rerun()
    except ConnectionError as e:
        st.session_state.pipeline_error = f"Network error: {e}. Check API keys."
        st.rerun()
    except Exception as e:
        st.session_state.pipeline_error = f"Pipeline failed: {e}"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  RESULTS DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def _display_results(result: dict) -> None:
    decision = result.get("decision", {})
    trace = result.get("trace", {})

    # ── Top: Decision Banner ─────────────────────────────────────────────────
    _show_decision_banner(decision)

    # ── Main Layout ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns([0.62, 0.38], gap="medium")

    with col_left:
        _show_agent_reasoning(trace)
        _show_decision_pipeline(trace)

    with col_right:
        _show_risk_panel(trace)
        _show_data_sources(trace)
        _show_journal_footer(result)


# ═══════════════════════════════════════════════════════════════════════════════
#  COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def _show_decision_banner(decision: dict) -> None:
    d = decision.get("decision", "HOLD")
    color_map = {"BUY": "#00c853", "SELL": "#ff1744", "HOLD": "#ffab00"}
    bg_map = {"BUY": "#003d1a", "SELL": "#3d0000", "HOLD": "#3d2e00"}
    color = color_map.get(d, "#666")
    bg = bg_map.get(d, "#1a1a2e")

    confidence = decision.get("confidence", 0.5)
    rationale = decision.get("decision_rationale", "")
    risk_overridden = decision.get("is_risk_overridden", False)

    st.markdown(
        f"""
        <div class="decision-banner" style="border-left-color: {color}; background: {bg};">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <h1 style="color: {color};">{d}</h1>
                    <div class="meta">Confidence: {confidence:.0%}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; color:#888;">Signal</div>
                    <div style="font-size:1.5rem; font-weight:700; color: {color};">{d}</div>
                </div>
            </div>
            <div class="meta" style="margin-top:0.6rem;">
                {rationale[:200]}
                {'[Risk Override Active]' if risk_overridden else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _show_agent_reasoning(trace: list) -> None:
    st.markdown('<div class="section-title">Agent Reasoning</div>', unsafe_allow_html=True)

    agent_styles = {
        "research": {"color": "#00bcd4", "icon": "01", "title": "Research"},
        "quant": {"color": "#7c4dff", "icon": "02", "title": "Quant"},
        "risk": {"color": "#ff6d00", "icon": "03", "title": "Risk"},
        "executor": {"color": "#00e676", "icon": "04", "title": "Executor"},
    }

    for agent_result in trace:
        name = agent_result.get("agent_name", "?")
        confidence = agent_result.get("confidence", 0)
        reasoning = agent_result.get("reasoning", "")
        output = agent_result.get("output", {})
        style = agent_styles.get(name, {"color": "#888", "icon": "?", "title": name.title()})

        st.markdown(
            f"""
            <div class="agent-card" style="border-left-color: {style['color']};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="agent-name" style="color: {style['color']};">
                            {style['icon']} {style['title']} Agent
                        </span>
                        <span class="agent-conf">Confidence: {confidence:.0%}</span>
                    </div>
                </div>
                <div class="agent-reasoning">{reasoning}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Agent-specific details
        if name == "quant":
            cs = output.get("composite_score", 0)
            signal = output.get("signal", "?")
            cols = st.columns(5, gap="small")
            cols[0].metric("Score", f"{cs:.0f}/100", help="Composite score")
            cols[1].metric("RSI(14)", f"{output.get('rsi_14', 0):.1f}", help="Relative Strength Index")
            cols[2].metric("ADX", f"{output.get('adx_14', 0):.1f}", help="Average Directional Index")
            cols[3].metric("ATR", f"{output.get('atr_14', 0):.2f}", help="Average True Range")
            sig_col = "green" if signal == "bullish" else ("red" if signal == "bearish" else "gray")
            cols[4].markdown(f"**Signal**<br><span style='color:{sig_col};font-weight:600;'>{signal.upper()}</span>",
                             unsafe_allow_html=True)

        elif name == "risk":
            rr = output
            cols = st.columns(4, gap="small")
            cols[0].metric("VaR(95%)", f"{rr.get('var_95', 0):.2%}", help="Value at Risk")
            cols[1].metric("CVaR", f"{rr.get('cvar_95', 0):.2%}", help="Conditional VaR")
            cols[2].metric("Kelly", f"{rr.get('kelly_fraction', 0):.2f}", help="Kelly Criterion")
            safe = rr.get("is_safe", True)
            safe_text = "Safe" if safe else "Risk"
            safe_color = "green" if safe else "red"
            cols[3].markdown(f"**Status**<br><span style='color:{safe_color};font-weight:600;'>{safe_text}</span>",
                             unsafe_allow_html=True)


def _show_decision_pipeline(trace: list) -> None:
    st.markdown('<div class="section-title">Decision Pipeline</div>', unsafe_allow_html=True)

    steps = []
    for agent_result in trace:
        name = agent_result.get("agent_name", "?")
        confidence = agent_result.get("confidence", 0)
        d = agent_result.get("output", {}).get("decision", "")
        steps.append({
            "Step": name.title(),
            "Confidence": f"{confidence:.0%}",
            "Influence": "Decision" if name == "executor" else "Signal",
        })

    if steps:
        st.dataframe(
            pd.DataFrame(steps),
            hide_index=True,
            column_config={
                "Step": st.column_config.TextColumn("Agent"),
                "Confidence": st.column_config.TextColumn("Confidence", width="small"),
                "Influence": st.column_config.TextColumn("Role", width="small"),
            },
        )


def _show_risk_panel(trace: list) -> None:
    st.markdown('<div class="section-title">Risk Dashboard</div>', unsafe_allow_html=True)

    risk_output = {}
    for t in trace:
        if t.get("agent_name") == "risk":
            risk_output = t.get("output", {})
            break

    if risk_output:
        var_95 = risk_output.get("var_95", 0)
        var_99 = risk_output.get("var_99", 0)
        cvar = risk_output.get("cvar_95", 0)
        kelly = risk_output.get("kelly_fraction", 0)

        cols = st.columns(2, gap="small")
        cols[0].metric("VaR(95%)", f"{var_95:.2%}", "Daily loss threshold")
        cols[1].metric("VaR(99%)", f"{var_99:.2%}", "Extreme loss threshold")

        cols = st.columns(2, gap="small")
        cols[0].metric("CVaR(95%)", f"{cvar:.2%}", "Expected shortfall")
        cols[1].metric("Kelly Fraction", f"{kelly:.2f}", "Optimal position size")

        max_pos = risk_output.get("max_position", 0)
        port_val = risk_output.get("portfolio_value", 0)
        if port_val:
            exposure = (max_pos / port_val) * 100
            st.progress(min(exposure / 100, 1.0), text=f"Max Exposure: {exposure:.1f}%")

        cb = risk_output.get("circuit_breaker_active", False)
        if cb:
            st.warning("Circuit Breaker ACTIVE — all positions on hold", icon="⚠️")
        else:
            st.caption("Circuit Breaker: Inactive")
    else:
        st.info("No risk data available.")


def _show_data_sources(trace: list) -> None:
    st.markdown('<div class="section-title">Data Sources</div>', unsafe_allow_html=True)

    research_output = {}
    for t in trace:
        if t.get("agent_name") == "research":
            research_output = t.get("output", {})
            break

    if research_output:
        quality = research_output.get("data_quality", "unknown")
        quality_color = {"excellent": "green", "good": "green", "fair": "orange", "unknown": "gray"}
        st.markdown(
            f"Data Quality: "
            f"<span style='color:{quality_color.get(quality, 'gray')};'>{quality.title()}</span>",
            unsafe_allow_html=True,
        )

        price_data = research_output.get("price_data", {})
        if price_data:
            current = price_data.get("current", 0)
            change = price_data.get("change_24h", 0)
            h24 = price_data.get("high_24h", 0)
            l24 = price_data.get("low_24h", 0)

            metrics = st.columns(2, gap="small")
            metrics[0].metric("Price", f"${current:.2f}")
            delta_color = "inverse" if change < 0 else "normal"
            metrics[1].metric("24h Change", f"{change:+.2f}%", delta=f"{abs(change):.2f}%",
                              delta_color=delta_color)

            metrics = st.columns(2, gap="small")
            metrics[0].metric("24h High", f"${h24:.2f}")
            metrics[1].metric("24h Low", f"${l24:.2f}")
    else:
        st.caption("Using mock data (no external APIs)")


def _show_journal_footer(result: dict) -> None:
    journal_count = result.get("journal_entries", 0)
    st.sidebar.metric("Journal Entries", journal_count)

    journal_path = Path.home() / ".kairos" / "demo_journal.json"
    if journal_path.exists():
        st.sidebar.caption(f"Journal: {journal_path.name}")
        if st.sidebar.button("Clear Journal"):
            journal_path.unlink(missing_ok=True)
            st.rerun()


if __name__ == "__main__":
    run()
