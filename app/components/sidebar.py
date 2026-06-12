"""Left sidebar - control panel: profile form, KB management, quick actions, query box."""

import time

import streamlit as st

from app.prolog_engine import FinanceEngine, PrologQueryError
from app.utils.formatting import format_query_result
from app.utils.state import (
    add_query_history,
    set_analysis,
    set_profile_loaded,
    set_prefill_query,
)

OCCUPATIONS = ["student", "employed", "self_employed", "retired", "unemployed"]
GOALS = ["buy_house", "retire_early", "pay_debt", "education", "invest", "travel"]


def _profile_form(engine: FinanceEngine) -> None:
    st.subheader("User Profile")
    with st.form("user_profile"):
        age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)
        occupation = st.selectbox("Occupation", OCCUPATIONS)
        income = st.number_input("Monthly income", min_value=0.0, value=0.0, step=100.0)
        needs = st.number_input("Monthly needs expenses", min_value=0.0, value=0.0, step=100.0)
        wants = st.number_input("Monthly wants expenses", min_value=0.0, value=0.0, step=100.0)
        emergency_fund = st.number_input("Emergency fund balance", min_value=0.0, value=0.0, step=100.0)
        investment = st.number_input("Investment balance", min_value=0.0, value=0.0, step=100.0)
        goal = st.selectbox("Goal", GOALS)

        submitted = st.form_submit_button("Submit Profile")
        if submitted:
            engine.load_profile(
                age=age, occupation=occupation, income=income,
                needs=needs, wants=wants,
                emergency_fund=emergency_fund, investment=investment,
                goal=goal,
            )
            set_profile_loaded(True)
            set_analysis(None)
            st.success("Profile loaded into the knowledge base.")
            st.rerun()


def _kb_management(engine: FinanceEngine) -> None:
    st.subheader("Knowledge Base Management")

    with st.form("add_fact_form"):
        fact = st.text_input(
            "Add Fact",
            placeholder="debt(user, credit_card, 50000, 24)",
        )
        if st.form_submit_button("Assert Fact") and fact:
            try:
                engine.assert_fact(fact)
                set_analysis(None)
                st.success(f"Asserted: {fact}")
            except PrologQueryError as exc:
                st.error(str(exc))

    with st.form("remove_fact_form"):
        fact = st.text_input(
            "Remove Fact",
            placeholder="debt(user, credit_card, 50000, 24)",
        )
        if st.form_submit_button("Retract Fact") and fact:
            try:
                ok = engine.retract_fact(fact)
                set_analysis(None)
                if ok:
                    st.success(f"Retracted: {fact}")
                else:
                    st.warning("No matching fact found.")
            except PrologQueryError as exc:
                st.error(str(exc))


def _quick_actions(engine: FinanceEngine) -> dict:
    st.subheader("Quick Actions")
    actions = {
        "run": st.button("Run Recommendation", width="stretch"),
        "kb": st.button("Show Knowledge Base", width="stretch"),
        "dynamic": st.button("Show Dynamic Facts", width="stretch"),
        "explain": st.button("Explain Result", width="stretch"),
    }

    if actions["run"]:
        set_analysis({
            "health": engine.financial_health(),
            "gates": engine.gate_statuses(),
            "metrics": engine.metrics(),
            "recommendations": engine.recommendations(),
            "top": engine.top_recommendation(),
        })
        st.rerun()

    if actions["kb"]:
        st.toast("Knowledge Base Viewer: see the 'All' tab in Section 2.")

    if actions["dynamic"]:
        st.toast("Knowledge Base Viewer: see the 'Dynamic Facts' tab in Section 2.")

    if actions["explain"]:
        st.session_state["explanation_expanded"] = True

    return actions


def _query_console_input(engine: FinanceEngine) -> None:
    st.subheader("Custom Prolog Query")
    query_text = st.text_area(
        "Query",
        value=st.session_state.get("prefill_query", ""),
        placeholder="financial_health(user, X)",
        key="query_input",
    )

    if st.button("Run Query", width="stretch"):
        if not query_text.strip():
            st.warning("Enter a query first.")
        else:
            start = time.perf_counter()
            try:
                rows = engine.raw_query(query_text)
                result = format_query_result(rows)
            except PrologQueryError as exc:
                result = f"Error: {exc}"
            elapsed_ms = (time.perf_counter() - start) * 1000
            add_query_history(query_text.strip(), result, elapsed_ms)
            set_prefill_query("")
            st.rerun()


def render(engine: FinanceEngine) -> dict:
    with st.sidebar:
        _profile_form(engine)
        st.divider()
        _kb_management(engine)
        st.divider()
        actions = _quick_actions(engine)
        st.divider()
        _query_console_input(engine)
    return actions
