"""Personal Finance Advisor - Streamlit dashboard entry point.

Run with: streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

# `streamlit run` only puts this file's directory (app/) on sys.path, not
# the project root - add the root so `app.*` imports resolve as a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.components import (
    explanation_panel,
    inference_panel,
    kb_overview,
    kb_viewer,
    query_console,
    sidebar,
)
from app.prolog_engine import FinanceEngine
from app.utils.state import init_state


@st.cache_resource
def get_engine() -> FinanceEngine:
    return FinanceEngine()


def main() -> None:
    st.set_page_config(
        page_title="Personal Finance Advisor",
        layout="wide",
    )
    init_state()

    st.title("Personal Finance Advisor")
    st.caption("A rule-based expert system using the Financial Order of Operations (FOO).")

    engine_error = None
    try:
        engine = get_engine()
    except Exception as exc:  # pyswip/SWI-Prolog not available or KB load failed
        engine_error = str(exc)
        engine = None

    if engine_error:
        st.error(f"Engine Error: {engine_error}")
        st.stop()

    sidebar.render(engine)

    kb_overview.render(engine, engine_error)
    st.divider()
    kb_viewer.render(engine)
    st.divider()
    inference_panel.render(engine)
    st.divider()
    explanation_panel.render(engine)
    st.divider()
    query_console.render()


if __name__ == "__main__":
    main()
