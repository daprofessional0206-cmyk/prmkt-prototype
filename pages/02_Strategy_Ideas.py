from __future__ import annotations
import streamlit as st
from dataclasses import asdict
from shared import ui, state, history
from shared import llm

st.set_page_config(page_title="Strategy Ideas", page_icon="💡", layout="wide")
ui.inject_css()
ui.page_title("Strategy Ideas", "Brainstorm bold PR & marketing angles quickly.")

state.init()
co = state.get_company()

with st.container():
    goals = st.text_area("Business Goals (optional override)", value="", placeholder=co.goals or "", height=100)

cols = st.columns(2)
with cols[0]:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
with cols[1]:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

if st.button("✨ Generate Strategy Idea", type="primary"):
    idea, err = llm.strategy(goals.strip(), co, tone, length)

    history.add_history(
        "strategy",
        payload={"tone": tone, "length": length, "goals": goals.strip() or co.goals, "company": asdict(co)},
        result=idea,
        tags=["strategy", tone, length],
    )

    if err:
        st.error("Could not generate right now. LLM may be rate-limited or key invalid. See Admin Settings → OpenAI.")
        with st.expander("Fallback idea (generated locally)"):
            st.write(idea)
        st.caption(f"Details: {err}")
    else:
        st.success("Strategy generated!")
        st.write(idea)
