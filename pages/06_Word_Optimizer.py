# pages/06_Word_Optimizer.py
from __future__ import annotations
import streamlit as st
from shared import ui, state, history
from shared.llm import llm_copy

state.init()
ui.page_title("Word Optimizer", "Rewrite + suggest stronger wording (Grammarly++ vibe).")

co = state.get_company()
goal = st.selectbox("Goal", ["Clarity","Persuasion","SEO","Trust"], index=1)
tone = st.selectbox("Tone", ["Professional","Friendly","Bold","Neutral"], index=0)
lang = st.selectbox("Language", ["English","Spanish","French","German"], index=0)

src = st.text_area("Paste your copy", height=180, value="Acme RoboHub 2.0 speeds onboarding and lowers costs for modern teams.")
c1, c2, c3 = st.columns(3)
with c1:
    do_rewrite = st.button("Rewrite")
with c2:
    do_suggest = st.button("Suggest better words")
with c3:
    clear = st.button("Clear output")

if "wo_out" not in st.session_state:
    st.session_state["wo_out"] = ""

if do_rewrite:
    prompt = f"Rewrite the following in {lang}, tone {tone}, optimized for {goal}. Keep it concise.\n\nText:\n{src}"
    out = llm_copy(prompt, temperature=0.55, max_tokens=400)
    st.session_state["wo_out"] = out
    history.add("optimizer", out, {"mode":"rewrite","src":src,"tone":tone,"goal":goal,"lang":lang},
                tags=["optimizer","rewrite", goal, tone, lang], meta={"company": co.name})

if do_suggest:
    prompt = f"Suggest 10 stronger word/phrase replacements (term → replacement) in {lang}, tone {tone}, for this text:\n{src}"
    out = llm_copy(prompt, temperature=0.5, max_tokens=400)
    st.session_state["wo_out"] = out
    history.add("optimizer", out, {"mode":"suggest","src":src,"tone":tone,"goal":goal,"lang":lang},
                tags=["optimizer","suggestions", tone, lang], meta={"company": co.name})

if clear:
    st.session_state["wo_out"] = ""

st.markdown("### Output")
st.markdown(st.session_state["wo_out"])
