# pages/02_Strategy_Ideas.py
from __future__ import annotations

import streamlit as st

from shared.state import get_company
from shared.llm import llm_copy, is_openai_ready
from shared.history import add_history


st.set_page_config(page_title="Strategy Ideas", page_icon="💡", layout="wide")

st.title("💡 Strategy Ideas")
st.caption("Brainstorm bold PR & marketing angles quickly.")

co = get_company()
goals = st.text_area("Business Goals (optional override)", value="", height=90)

col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Tone", ["Professional", "Neutral", "Playful", "Bold"], index=0)
with col2:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

gen = st.button("✨ Generate Strategy Idea", type="primary", use_container_width=True)

# throttle guard UX
if "last_strategy_ts" not in st.session_state:
    st.session_state["last_strategy_ts"] = 0.0

if gen:
    if not is_openai_ready():
        st.error("OpenAI key not found. Set it in **Admin Settings → How to set the key**.")
        st.stop()

    last_err = None  # IMPORTANT: avoid 'last_err referenced before assignment'
    try:
        # prompt
        ask_goals = goals.strip() or co.goals
        prompt = (
            f"You are a senior PR/Marketing strategist. Company: {co.name} "
            f"(Industry: {co.industry}, Size: {co.size}).\n"
            f"Business goals: {ask_goals}\n"
            f"Write ONE practical campaign or PR idea. "
            f"Tone: {tone}. Length: {length}. Output 4–6 bullets: Objective, Insight, Big Idea, Why it works, First steps."
        )

        out = llm_copy(prompt)
        st.success("Idea created!")
        st.markdown(out)

        add_history(
            "strategy",
            payload={"tone": tone, "length": length, "goals": ask_goals, "company": co.asdict()},
            output={"idea": out},
            tags=["strategy", tone],
        )

    except Exception as e:
        last_err = e
        st.error(
            "Could not generate right now. LLM may be rate-limited or the key is invalid. "
            "Check **Admin Settings → OpenAI** and try again."
        )
        # Safe fallback (so user still gets *something*)
        fallback = (
            "• Objective: Raise awareness among ICP this quarter\n"
            "• Insight: Decision-makers respond well to credible social proof\n"
            "• Big Idea: ‘Customer Proof Week’ — 5 short daily LinkedIn live chats with clients\n"
            "• Why it works: Authority + consistency builds momentum\n"
            "• First steps: shortlist 5 customers, book 20-min slots, create promo pack"
        )
        st.info("Fallback idea:")
        st.text(fallback)

        add_history(
            "strategy",
            payload={"tone": tone, "length": length, "goals": goals.strip(), "company": co.asdict()},
            output={"idea": fallback, "error": str(last_err)},
            tags=["strategy", "fallback"],
        )
