# pages/02_Strategy_Ideas.py
from __future__ import annotations
import streamlit as st
from shared import state, history
from typing import List
from datetime import datetime
# LLM
try:
    from shared.llm import llm_copy
    HAS_LLM = True
except Exception:
    HAS_LLM = False

st.set_page_config(page_title="Presence • Strategy Ideas", page_icon="💡", layout="wide")
state.init()

st.title("💡 Strategy Ideas")
st.caption("Brainstorm bold PR & marketing angles quickly.")

co = state.get_company()

with st.expander("Company context", expanded=False):
    st.write(f"**Name:** {co.get('name')}")
    st.write(f"**Industry:** {co.get('industry')}, **Size:** {co.get('size')}")
    st.write(f"**Goals:** {co.get('goals')}")

goals = st.text_area(
    "Business goals (edit as needed)",
    value=co.get("goals", ""),
    height=90,
)

tone = st.selectbox("Tone", ["Professional", "Bold", "Friendly", "Neutral"], index=0)
length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)
primary_channel = st.selectbox("Primary channel", ["PR", "LinkedIn", "Email", "Blog", "Instagram", "YouTube"])

prompt = f"""
Propose a practical PR/Marketing initiative for {co.get('name')} ({co.get('industry')}, size: {co.get('size')}).
Goals: {goals}.
Output a concise plan (5–7 bullets) with headline, rationale, primary channel, and success metrics.
Tone: {tone}. Length: {length}. Primary channel: {primary_channel}.
"""

if st.button("Generate strategy idea", type="primary"):
    try:
        if HAS_LLM and state.has_openai():
            idea = llm_copy(prompt, temperature=0.55, max_tokens=420)
        else:
            idea = (
                f"**Campaign Idea: “Momentum Now”**\n"
                f"- **Rationale:** Convert in-market demand with fast, helpful education.\n"
                f"- **Primary channel:** {primary_channel}.\n"
                f"- **Tactics:** Rapid Q&A posts, 2 customer mini-stories, founder AMAs.\n"
                f"- **Measurement:** CTR, demo requests, 30-day retention.\n"
                f"- **Notes:** Align tone to {co.get('size','').lower()} buyers in {co.get('industry','').lower()}."
            )
        st.success("Strategy idea created.")
        st.markdown(idea)

        # Unified history entry
        history.add(
            kind="strategy",
            payload={
                "company": co,
                "tone": tone,
                "length": length,
                "primary_channel": primary_channel,
                "goals": goals,
                "ts": datetime.now().isoformat(timespec="seconds")
            },
            output=idea,
            tags=["strategy", primary_channel, tone, length]
        )
    except Exception as e:
        st.error(f"Error generating idea: {e}")
