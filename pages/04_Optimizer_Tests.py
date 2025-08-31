# pages/04_Optimizer_Tests.py
from __future__ import annotations
import streamlit as st
from shared import ui, state, history
from shared.llm import llm_copy

state.init()
ui.page_title("Optimizer Tests (A/B scoring)", "Try small variations and get heuristic scores.")

co = state.get_company()

text = st.text_area("Base copy", height=140, value="Meet RoboHub 2.0 — faster setup, SOC 2 Type II, and 30% lower cost.")
tone = st.selectbox("Tone", ["Professional","Friendly","Bold","Neutral"], index=0)
goal = st.selectbox("Goal", ["Awareness","Clicks","Signups","Demo Requests"], index=3)
lang = st.selectbox("Language", ["English","Spanish","French","German"], index=0)

if st.button("Generate & Score Variants", type="primary"):
    prompt = f"""Create 3 short variants (A/B/C) of this copy in {lang}, tone {tone}, optimized for {goal}.
Return in the format:
A) <one paragraph up to 2 lines>
B) ...
C) ...
After that, rate each A/B/C from 1–10 for {goal} with a brief reason."""
    out = llm_copy(prompt, temperature=0.6, max_tokens=800)
    st.success("Generated")
    st.markdown(out)

    history.add(
        kind="optimizer",
        text=out,
        payload={"goal": goal, "tone": tone, "language": lang, "base": text},
        tags=["optimizer", goal, tone, lang],
        meta={"company": co.name}
    )
