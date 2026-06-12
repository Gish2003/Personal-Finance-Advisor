"""st.session_state helpers.

Streamlit reruns the whole script on every interaction, so anything that
must survive a rerun (query history, last analysis results, whether a
profile has been loaded) is kept here rather than in module globals.
"""

import streamlit as st

QUERY_HISTORY_KEY = "query_history"
ANALYSIS_KEY = "analysis"
PROFILE_LOADED_KEY = "profile_loaded"
PREFILL_QUERY_KEY = "prefill_query"

MAX_HISTORY = 10


def init_state() -> None:
    if QUERY_HISTORY_KEY not in st.session_state:
        st.session_state[QUERY_HISTORY_KEY] = []
    if ANALYSIS_KEY not in st.session_state:
        st.session_state[ANALYSIS_KEY] = None
    if PROFILE_LOADED_KEY not in st.session_state:
        st.session_state[PROFILE_LOADED_KEY] = False
    if PREFILL_QUERY_KEY not in st.session_state:
        st.session_state[PREFILL_QUERY_KEY] = ""


def set_profile_loaded(loaded: bool = True) -> None:
    st.session_state[PROFILE_LOADED_KEY] = loaded


def is_profile_loaded() -> bool:
    return st.session_state.get(PROFILE_LOADED_KEY, False)


def set_analysis(analysis: dict) -> None:
    st.session_state[ANALYSIS_KEY] = analysis


def get_analysis() -> dict | None:
    return st.session_state.get(ANALYSIS_KEY)


def add_query_history(query: str, result: str, elapsed_ms: float) -> None:
    history = st.session_state.setdefault(QUERY_HISTORY_KEY, [])
    history.insert(0, {
        "timestamp": _now(),
        "query": query,
        "result": result,
        "elapsed_ms": elapsed_ms,
    })
    del history[MAX_HISTORY:]


def get_query_history() -> list[dict]:
    return st.session_state.get(QUERY_HISTORY_KEY, [])


def set_prefill_query(query: str) -> None:
    st.session_state[PREFILL_QUERY_KEY] = query


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")
