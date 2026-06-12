"""Section 3 - Inference Results: health badge, FOO gates, metrics, recommendations."""

import streamlit as st

from app.prolog_engine import FinanceEngine
from app.utils.formatting import (
    badge_html,
    format_currency,
    format_months,
    format_percent,
    format_status_label,
    gate_icon_color,
    health_color,
    step_name,
)
from app.utils.state import get_analysis, is_profile_loaded, set_analysis


def _run_analysis(engine: FinanceEngine) -> dict:
    return {
        "health": engine.financial_health(),
        "gates": engine.gate_statuses(),
        "metrics": engine.metrics(),
        "recommendations": engine.recommendations(),
        "top": engine.top_recommendation(),
    }


def render(engine: FinanceEngine) -> None:
    st.subheader("3. Inference Results")

    if not is_profile_loaded():
        st.info("Submit the user profile form in the sidebar, then click "
                "**Run Recommendation** to see results here.")
        return

    analysis = get_analysis()
    if analysis is None:
        analysis = _run_analysis(engine)
        set_analysis(analysis)

    # --- Composite health badge -----------------------------------
    health = analysis["health"]
    color = health_color(health)
    st.markdown(
        f"**Overall Financial Health:** "
        + badge_html(format_status_label(health), color),
        unsafe_allow_html=True,
    )

    st.markdown("&nbsp;", unsafe_allow_html=True)

    # --- FOO gate status pills --------------------------------------
    st.markdown("**FOO Gate Status**")
    gates = analysis["gates"]
    gate_order = [
        ("budget", "Budget"),
        ("debt", "Debt"),
        ("emergency", "Emergency"),
        ("savings", "Savings"),
        ("investment", "Investment"),
    ]
    cols = st.columns(5)
    for col, (key, label) in zip(cols, gate_order):
        status = gates[key]["status"]
        icon, color = gate_icon_color(status)
        col.markdown(
            f"<div style='text-align:center'>"
            f"<div style='font-size:1.5em'>{icon}</div>"
            f"<div><strong>{label}</strong></div>"
            f"<div style='color:{color}'>{format_status_label(status)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("&nbsp;", unsafe_allow_html=True)

    # --- Key metrics --------------------------------------------------
    st.markdown("**Key Metrics**")
    metrics = analysis["metrics"]
    mcols = st.columns(4)
    mcols[0].metric("Savings Rate", format_percent(metrics["savings_rate"]))
    mcols[1].metric("Debt-to-Income", format_percent(metrics["debt_to_income"]))
    mcols[2].metric("Net Worth", format_currency(metrics["net_worth"]))
    mcols[3].metric("Emergency Fund Coverage", format_months(metrics["emergency_fund_months"]))

    st.markdown("&nbsp;", unsafe_allow_html=True)

    # --- Ranked recommendations ---------------------------------------
    st.markdown("**Ranked Recommendations**")
    recommendations = analysis["recommendations"]
    top = analysis["top"]

    if not recommendations:
        st.success("No outstanding recommendations - all FOO gates clear.")
    else:
        for step, action in recommendations:
            is_top = action == top
            prefix = "⭐ **TOP**" if is_top else f"Step {step}"
            label = f"**{prefix} - {step_name(step)}**: {action}"
            if is_top:
                st.markdown(
                    f"<div style='border-left:4px solid {health_color('good')};"
                    f"padding:0.5em 1em;background-color:rgba(22,163,74,0.08)'>"
                    f"{label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(label)
