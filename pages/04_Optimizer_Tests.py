# pages/04_Optimizer_Tests.py
from __future__ import annotations
import streamlit as st
from shared import state
from shared.llm import is_openai_ready, llm_copy

state.init()
st.set_page_config(page_title="Optimizer Tests", layout="wide")
st.title("🧪 Optimizer Tests")
st.caption("Test different tones, lengths, or styles to optimize messaging.")

ok, remaining = state.can_generate(3)
if not ok:
    st.info(f"Please wait {remaining}s before generating again.")
    st.stop()

if not is_openai_ready():
    st.warning("OpenAI key not configured. Set it in environment/Streamlit secrets.")
    st.stop()

base = st.text_area("Base copy", height=120, placeholder="Paste your base copy here…")
tone = st.selectbox("Try another tone", ["Bold", "Friendly", "Formal", "Playful"])
length = st.selectbox("Try another length", ["Short", "Medium", "Long"])

if st.button("Generate Variations"):
    prompt = f"Rewrite the following copy. Tone: {tone}. Length: {length}.\n\nCopy:\n{base}"
    try:
        v = llm_copy(prompt).strip()
        st.success("Variants created!")
        st.markdown(v)
        state.add_history("optimize", {"base": base, "tone": tone, "length": length}, v, tags=["optimize", tone, length])
    except Exception as e:
        st.error(str(e))
