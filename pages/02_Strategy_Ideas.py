# pages/02_Strategy_Ideas.py
from __future__ import annotations
import streamlit as st
from shared import state
from shared.llm import is_openai_ready, llm_copy

state.init()
st.set_page_config(page_title="Strategy Ideas", layout="wide")
st.title("💡 Strategy Ideas")
st.caption("Brainstorm bold PR & marketing angles quickly.")

ok, remaining = state.can_generate(4)
if not ok:
    st.info(f"Please wait {remaining}s before generating again.")
    st.stop()

if not is_openai_ready():
    st.warning("OpenAI key not configured. Set it in environment/Streamlit secrets.")
    st.stop()

company = state.get_company()
rules = state.get_brand_rules()

prompt = f"""
Suggest 5 concise PR/marketing strategy ideas.

Company: {company.get('name','')}
Industry: {company.get('industry','')}
Size: {company.get('size','')}
Goals: {company.get('goals','')}
Brand rules (optional): {rules if rules else '—'}

Output as a short numbered list (1–5), each idea in 1–2 sentences.
"""

try:
    ideas = llm_copy(prompt).strip()
    st.success("Ideas generated!")
    st.markdown(ideas)
    state.add_history("strategy", {"prompt": prompt}, ideas, tags=["strategy"])
except Exception as e:
    st.error(str(e))
