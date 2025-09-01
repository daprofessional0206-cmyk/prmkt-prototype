# pages/07_PR_Intelligence.py (top part only – rest of your page can stay)
from __future__ import annotations
import streamlit as st

from shared import state
from shared.llm import llm_copy
from shared.history import add_history

def co_val(co, key: str, default: str = "") -> str:
    """Read from dataclass or dict safely."""
    if co is None:
        return default
    try:
        v = getattr(co, key)
        return "" if v is None else str(v)
    except Exception:
        try:
            v = co.get(key, default)  # type: ignore[union-attr]
            return "" if v is None else str(v)
        except Exception:
            return default

st.set_page_config(page_title="PR Intelligence (v1)", page_icon="📣")
st.title("📣 PR Intelligence (v1)")
st.caption("Get press-worthy story angles, target beats, timing windows, and one-line pitches.")

state.init()
co = state.get_company()

timing = st.selectbox("Timing preference", ["ASAP (next 7 days)", "Soon (2–4 weeks)", "This quarter", "No specific timing"])

st.write(
    f"**Context** — Company: {co_val(co, 'name')} | Industry: {co_val(co, 'industry')} | Audience: {co_val(co, 'audience')}"
)

# ... keep your existing body/generation UI below ...
