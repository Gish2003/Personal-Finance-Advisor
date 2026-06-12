"""Section 4 - Explanation Panel: reasoning trace for the top recommendation."""

import streamlit as st

from app.prolog_engine import FinanceEngine
from app.utils.formatting import format_status_label, health_color, step_name
from app.utils.state import get_analysis, is_profile_loaded

_GATE_LABELS = [
    ("budget", 1, "Budget (50/30/20)"),
    ("debt", 2, "High-Interest Debt"),
    ("emergency", 3, "Emergency Fund"),
    ("savings", 4, "Savings Rate"),
    ("investment", 5, "Investment Readiness"),
]

_GATE_PREDICATES = {
    "budget": "budget_gate_passed",
    "debt": "debt_gate_passed",
    "emergency": "emergency_gate_passed",
    "savings": "savings_gate_passed",
    "investment": "investment_ready",
}


def _first_failed_gate(gates: dict):
    for key, step, label in _GATE_LABELS:
        if not gates[key]["passed"]:
            return key, step, label
    return None


def render(engine: FinanceEngine) -> None:
    st.subheader("4. Explanation Panel")

    if not is_profile_loaded():
        st.info("Run a recommendation first to see the reasoning trace.")
        return

    analysis = get_analysis()
    if analysis is None:
        st.info("Click **Run Recommendation** in the sidebar to populate this section.")
        return

    gates = analysis["gates"]
    health = analysis["health"]
    top = analysis["top"]
    recommendations = analysis["recommendations"]

    # --- Why this was selected -----------------------------------------
    st.markdown("**Why this was selected**")
    failed = _first_failed_gate(gates)
    if failed is None:
        st.write(
            "All five FOO gates pass. The advisor recommends maintaining "
            "current habits, guided by your stated goal."
        )
    else:
        key, step, label = failed
        status = format_status_label(gates[key]["status"])
        st.write(
            f"The **{label}** gate (FOO step {step}) is the first gate that "
            f"has not been passed (status: *{status}*). Per the Financial "
            f"Order of Operations, every earlier gate must pass before a "
            f"later one is considered, so this step's recommendation takes "
            f"priority:"
        )
    st.markdown(f"> {top}")

    # --- Rules that succeeded / failed ----------------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Rules that succeeded**")
        passed_any = False
        for key, step, label in _GATE_LABELS:
            if gates[key]["passed"]:
                passed_any = True
                st.markdown(f"- ✅ `{_GATE_PREDICATES[key]}` - {label} "
                            f"({format_status_label(gates[key]['status'])})")
        if not passed_any:
            st.write("None of the gates currently pass.")

    with col2:
        st.markdown("**Rules that failed**")
        failed_any = False
        for key, step, label in _GATE_LABELS:
            if not gates[key]["passed"]:
                failed_any = True
                st.markdown(f"- ❌ `{_GATE_PREDICATES[key]}` - {label} "
                            f"({format_status_label(gates[key]['status'])})")
        if not failed_any:
            st.write("None - every gate passes.")

    # --- Final classification --------------------------------------------
    st.markdown("**Final classification**")
    color = health_color(health)
    st.markdown(
        f"<span style='color:{color};font-weight:700'>"
        f"{format_status_label(health)}</span> - derived from the combined "
        f"status of all five FOO gates above.",
        unsafe_allow_html=True,
    )

    # --- Full derivation trace ----------------------------------------------
    expanded = st.session_state.pop("explanation_expanded", False)
    with st.expander("Full derivation trace", expanded=expanded):
        st.write("Gate-by-gate status (in FOO priority order):")
        for key, step, label in _GATE_LABELS:
            passed = gates[key]["passed"]
            status = format_status_label(gates[key]["status"])
            mark = "✅ pass" if passed else "❌ fail"
            st.markdown(f"{step}. **{label}** - {status} - {mark}")

        st.write("All `recommend_step/3` clauses that matched:")
        if recommendations:
            for step, action in recommendations:
                marker = " (selected as top)" if action == top else ""
                st.markdown(f"- Step {step} ({step_name(step)}): {action}{marker}")
        else:
            st.write("(none - all gates clear)")
