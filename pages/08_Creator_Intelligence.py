# pages/08_Creator_Intelligence.py (top part only – rest can stay)
from __future__ import annotations
import streamlit as st

from shared import state
from shared.llm import llm_copy
from shared.history import add_history

def co_val(co, key: str, default: str = "") -> str:
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

st.set_page_config(page_title="Creator Intelligence", page_icon="🎬")
st.title("🎬 Creator Intelligence")

state.init()
co = state.get_company()

platform = st.selectbox("Platform", ["Instagram Reels","YouTube Shorts","TikTok","LinkedIn video"])
niche = st.text_input("Niche / theme", value=co_val(co, "audience", ""))
cta = st.text_input("Desired action (CTA)", value="Book a demo")
# ...rest continues
