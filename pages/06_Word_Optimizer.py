# pages/06_Word_Optimizer.py
from __future__ import annotations
import streamlit as st
from shared import state, history

try:
    from shared.llm import llm_copy
    HAS_LLM = True
except Exception:
    HAS_LLM = False

st.set_page_config(page_title="Presence • Word Optimizer", page_icon="🧠", layout="wide")
state.init()
co = state.get_company()

st.title("🧠 Word Optimizer (Rewrite & Improve)")
st.caption("Suggest stronger alternatives, clarity, and engagement improvements.")

input_text = st.text_area("Paste your copy to improve", height=180, placeholder="Paste here...")
goal = st.selectbox("Optimization goal", ["Clarity", "Persuasion", "SEO", "Engagement"])
tone = st.selectbox("Target tone", ["Professional", "Friendly", "Bold", "Neutral"])
lang = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0)

prompt = f"""
Rewrite the following copy for {goal} while keeping original meaning.
Target tone: {tone}. Language: {lang}.
Company: {co.get('name')} ({co.get('industry')}, {co.get('size')}).
Brand rules: {co.get('brand_rules','(none)')}

Original copy:
\"\"\"{input_text}\"\"\"

Return only the improved version.
"""

col = st.columns(3)
go = col[0].button("Rewrite", type="primary")
suggest = col[1].button("Suggest stronger words")
clear = col[2].button("Clear output")

if "optimizer_out" not in st.session_state:
    st.session_state["optimizer_out"] = ""

if go:
    if not input_text.strip():
        st.warning("Paste some text first.")
    else:
        if HAS_LLM and state.has_openai():
            out = llm_copy(prompt, temperature=0.4, max_tokens=600)
        else:
            out = input_text  # offline: echo (no-op)
        st.session_state["optimizer_out"] = out
        history.add(
            kind="optimizer",
            payload={"goal": goal, "tone": tone, "language": lang, "company": co},
            output=out,
            tags=["optimizer", goal, tone, lang],
        )

if suggest:
    if not input_text.strip():
        st.warning("Paste some text first.")
    else:
        if HAS_LLM and state.has_openai():
            out = llm_copy(
                f"Suggest stronger words/phrases for the following, keep meaning:\n\n{input_text}",
                temperature=0.5,
                max_tokens=400,
            )
        else:
            out = "• Improve verbs (e.g., “boost”, “streamline”) • Remove filler • Use active voice"
        st.session_state["optimizer_out"] = out
        history.add(
            kind="optimizer",
            payload={"goal": "Suggestions", "tone": tone, "language": lang, "company": co},
            output=out,
            tags=["optimizer", "suggestions", tone, lang],
        )

if clear:
    st.session_state["optimizer_out"] = ""
    st.experimental_rerun()  # ok to rerun here

st.subheader("Output")
st.markdown(st.session_state["optimizer_out"])
