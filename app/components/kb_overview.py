"""Section 1 - Knowledge Base Overview: four summary metric cards."""

import streamlit as st

from app.prolog_engine import FinanceEngine
from app.utils.state import is_profile_loaded


def render(engine: FinanceEngine, engine_error: str | None = None) -> None:
    st.subheader("1. Knowledge Base Overview")

    if engine_error:
        overview = {"total_facts": 0, "total_rules": 0, "dynamic_facts": 0}
        status_label, status_color = "Engine Error", "🔴"
    else:
        overview = engine.kb_overview()
        if not is_profile_loaded():
            status_label, status_color = "No Profile", "🟡"
        else:
            status_label, status_color = "Ready", "🟢"

    cols = st.columns(4)
    cols[0].metric("Total Facts", overview["total_facts"])
    cols[1].metric("Total Rules", overview["total_rules"])
    cols[2].metric("Dynamic Facts", overview["dynamic_facts"])
    cols[3].metric("System Status", f"{status_color} {status_label}")
