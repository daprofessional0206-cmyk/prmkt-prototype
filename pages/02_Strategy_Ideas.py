# pages/02_Strategy_Ideas.py
from __future__ import annotations
import streamlit as st
from shared import ui, state, history
from shared.llm import llm_copy
from shared.exports import text_to_docx_bytes, text_to_pdf_bytes

state.init()
ui.page_title("Strategy Ideas", "Brainstorm bold PR & marketing angles quickly.")

co = state.get_company()
col1, col2 = st.columns([2,1])
with col1:
    goals = st.text_area("Business Goals (edit if needed)", value=co.goals, height=110)
with col2:
    tone = st.selectbox("Tone", ["Professional","Friendly","Bold","Neutral"], index=0)
    length = st.selectbox("Length", ["Short","Medium","Long"], index=1)

if st.button("Generate Strategy Idea", type="primary"):
    prompt = f"""Propose a practical PR/Marketing initiative for {co.name} ({co.industry}, size: {co.size}).
Goals: {goals}.
Output a concise plan: headline, rationale, primary channel, 4–6 bullets, clear success metrics."""
    out = llm_copy(prompt, temperature=0.55, max_tokens=450)
    st.success("Generated")
    st.markdown(out)

    history.add(
        kind="strategy",
        text=out,
        payload={"tone": tone, "length": length, "goals": goals, "company": state.get_company_as_dict()},
        tags=["strategy", tone, length, co.size],
        meta={"company": co.name}
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download (.docx)", data=text_to_docx_bytes(out),
                           file_name="strategy_idea.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c2:
        st.download_button("Download (.pdf)", data=text_to_pdf_bytes(out),
                           file_name="strategy_idea.pdf", mime="application/pdf")
