from __future__ import annotations
import streamlit as st
from dataclasses import asdict
from shared import ui, state, history
from shared import llm

# ── Sidebar health badge (safe) ───────────────────────────────────────────────
import streamlit as st
try:
    from shared import state
    with st.sidebar:
        st.write(f"OpenAI: {'✅ Connected' if state.has_openai() else '❌ Missing'}")
except Exception:
    # Never crash the page if the helper isn't available
    with st.sidebar:
        st.write("OpenAI: status unavailable")

st.set_page_config(page_title="Optimizer Tests", page_icon="🧪", layout="wide")
ui.inject_css()
ui.page_title("Optimizer Tests", "Test different tones, lengths, or styles to optimize messaging.")

state.init()
co = state.get_company()

base_text = st.text_area("Base message (we will rewrite/compare)", height=150, placeholder="Paste any message or headline…")
cols = st.columns(2)
with cols[0]:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
with cols[1]:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=0)

if st.button("Run simple A/B test", type="primary"):
    # reuse content engine to produce 2 rewrites
    drafts, err = llm.variants("Rewrite / Improve", 2, co, tone, length, "English")
    history.add_history(
        "test",
        payload={"base": base_text, "tone": tone, "length": length, "company": asdict(co)},
        result=drafts,
        tags=["test", tone, length],
    )
    if err:
        st.error("LLM not available; showing simple fallback drafts.")
    for i, d in enumerate(drafts, 1):
        with st.expander(f"Candidate {i}"):
            st.write(d)
# ── Footer ────────────────────────────────────────────────────────────────────
import streamlit as st  # safe if already imported
st.caption("Presence — multi-page prototype (Phase 3.2 • build v3.2)")
