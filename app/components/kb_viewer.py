"""Section 2 - Knowledge Base Viewer: static rules / dynamic facts / all."""

import pandas as pd
import streamlit as st

from app.prolog_engine import FinanceEngine


def _to_dataframe(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["Predicate", "Arity", "Clause", "Module"])
    return pd.DataFrame(rows)[["Predicate", "Arity", "Clause", "Module"]]


def _filter(df: pd.DataFrame, search: str) -> pd.DataFrame:
    if not search:
        return df
    mask = df.apply(
        lambda col: col.astype(str).str.contains(search, case=False, regex=False)
    ).any(axis=1)
    return df[mask]


def render(engine: FinanceEngine) -> None:
    st.subheader("2. Knowledge Base Viewer")

    search = st.text_input("Search facts/rules", key="kb_viewer_search")

    static_rows = engine.static_clauses()
    dynamic_rows = engine.dynamic_clauses()

    static_df = _to_dataframe(static_rows)
    dynamic_df = _to_dataframe(dynamic_rows)
    all_df = _to_dataframe(static_rows + dynamic_rows)

    tabs = st.tabs(["Static Rules", "Dynamic Facts", "All"])

    with tabs[0]:
        df = _filter(static_df, search)
        st.dataframe(df, width="stretch", hide_index=True)

    with tabs[1]:
        df = _filter(dynamic_df, search)
        if df.empty:
            st.info("No dynamic facts asserted yet. Submit the profile form to populate the KB.")
        else:
            st.dataframe(df, width="stretch", hide_index=True)

    with tabs[2]:
        df = _filter(all_df, search)
        st.dataframe(df, width="stretch", hide_index=True)
