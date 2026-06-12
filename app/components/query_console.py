"""Section 5 - Prolog Query Console: read-only output + history."""

import streamlit as st

from app.utils.state import get_query_history

EXAMPLE_QUERIES = [
    "financial_health(user, X)",
    "findall(S-A, recommend_step(user, S, A), L)",
    "top_recommendation(user, A)",
    "all_debts(user, L)",
]


def render() -> None:
    st.subheader("5. Prolog Query Console")

    st.caption("Use the sidebar to run a custom query. Example queries:")
    cols = st.columns(len(EXAMPLE_QUERIES))
    for col, query in zip(cols, EXAMPLE_QUERIES):
        if col.button(query, key=f"example_{query}", width="stretch"):
            st.session_state["prefill_query"] = query
            st.rerun()

    history = get_query_history()
    if not history:
        st.info("No queries run yet.")
        return

    for entry in history:
        header = f"[{entry['timestamp']}] {entry['query']}  ({entry['elapsed_ms']:.1f} ms)"
        st.markdown(f"**{header}**")
        st.code(entry["result"], language="prolog")
