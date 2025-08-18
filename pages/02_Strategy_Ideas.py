# pages/02_Strategy_Ideas.py
from __future__ import annotations
import streamlit as st
from shared import state, ui
from shared.history import add as add_history
from shared.llm import llm_copy, is_openai_ready
from dataclasses import asdict
from shared.history import add_history  # or: from shared.history import add as add_history

state.init()
ui.title("Strategy Ideas")

co = state.get_company()

if st.button("Generate Strategy Idea"):
    prompt = f"""Propose a practical PR/Marketing initiative for {co.name} ({co.industry}, size: {co.size}).
Goals: {co.goals}.
Output a brief, 4–6 bullet plan with headline, rationale, primary channel, and success metrics."""
    try:
        idea = llm_copy(prompt, temperature=0.5, max_tokens=350) if is_openai_ready() else (
            f"**Campaign Idea: Momentum Now**\n- Rationale: practical, fast-moving education.\n- Primary channel: social + email.\n- Tactics: Q&A posts, mini-stories, AMA, ROI calc.\n- Metrics: CTR, demo requests, 30-day retention."
        )
        st.success("Idea generated.")
        st.markdown(idea)
        add_history(
    kind="strategy",
    payload=asdict(co),         # co is your Company dataclass instance
    output=idea,                # the generated idea text
    tags=["strategy"]           # optional tags (helps filtering later)
)
    except Exception as e:
        st.error(str(e))
