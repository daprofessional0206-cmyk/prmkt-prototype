# pages/02_Strategy_Ideas.py
from __future__ import annotations
import streamlit as st

from shared import state
from shared.history import add_history
from shared.llm import llm_copy  # your existing helper (online/offline inside)
from shared.exports import text_to_docx_bytes, text_to_pdf_bytes  # new export helpers

st.set_page_config(page_title="Presence • Strategy Ideas", page_icon="💡", layout="wide")

st.title("💡 Strategy Ideas")
st.caption("Brainstorm bold PR & marketing angles quickly.")

co = state.get_company_dict()

with st.expander("Company context", expanded=False):
    st.write(
        f"**Name:** {co['name']}  \n"
        f"**Industry:** {co['industry']}  \n"
        f"**Size:** {co['size']}  \n"
        f"**Goals:** {co['goals']}"
    )

col1, col2 = st.columns([1, 1])
with col1:
    tone = st.selectbox("Tone", ["Professional", "Conversational", "Bold"], index=0, key="si_tone")
with col2:
    length = st.selectbox("Length", ["Short", "Medium"], index=1, key="si_len")

goals = st.text_area(
    "Business goals (edit if needed)",
    value=co.get("goals", ""),
    height=90,
    key="si_goals",
)

if st.button("Generate Strategy Idea", type="primary", use_container_width=True):
    prompt = f"""
You are an expert PR/Marketing strategist. Propose a practical initiative for:
- Company: {co['name']} (Industry: {co['industry']}, Size: {co['size']})
- Business goals: {goals}

Output a brief plan in {length.lower()} length and {tone.lower()} tone:
- Headline
- Rationale
- Primary channel(s)
- 4–6 bullet tactics
- Success metrics
""".strip()

    try:
        idea = llm_copy(prompt, temperature=0.5, max_tokens=400)
        st.success("Strategy idea created.")
        st.markdown(idea)

        add_history(
            kind="strategy",
            payload={"tone": tone, "length": length, "goals": goals, "company": co},
            output=idea,
            tags=["strategy", tone, length],
        )

        # Downloads
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Download .docx",
                data=text_to_docx_bytes(idea, title="Strategy Idea"),
                file_name="strategy_idea.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        with c2:
            st.download_button(
                "Download .pdf",
                data=text_to_pdf_bytes(idea, title="Strategy Idea"),
                file_name="strategy_idea.pdf",
                mime="application/pdf",
            )
    except Exception as e:
        st.error(f"{e}")
