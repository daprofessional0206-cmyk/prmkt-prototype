# pages/02_Strategy_Ideas.py
from __future__ import annotations
import streamlit as st
from shared import state, llm, history
from shared.exports import text_to_docx_bytes, text_to_pdf_bytes

st.set_page_config(page_title="Strategy Ideas", page_icon="💡", layout="wide")
st.title("💡 Strategy Ideas")
st.caption("Brainstorm campaign angles & PR ideas tailored to your profile.")

state.init()
co = state.get_company()

goals = st.text_area(
    "Business Goals (optional override)",
    value=co.get("goals", "") if isinstance(co, dict) else getattr(co, "goals", ""),
    height=120,
    help="Tell me what matters now. Leave empty to use Company Profile goals.",
)

c1, c2, c3 = st.columns(3)
with c1:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
with c2:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)
with c3:
    lang = st.selectbox("Language", ["English"], index=0)

if "si_output" not in st.session_state:
    st.session_state["si_output"] = ""

if st.button("✨ Generate Strategy Idea", use_container_width=True):
    prompt = f"""You are a senior PR/Marketing strategist.
Company: {co.get('name','')} (Industry: {co.get('industry','')}, Size: {co.get('size','')}).
Audience: {co.get('audience','')}. Brand voice: {co.get('brand_voice','')}.
Goals: {goals.strip() or co.get('goals','')}

Write a {length.lower()} idea in a {tone.lower()} tone in {lang}.
Include: Objective, Core angle, 3–5 key tactics, and Success metrics."""
    try:
        out = llm.llm_copy(prompt)
        st.session_state["si_output"] = out
        history.add(
            tool="Strategy Ideas",
            payload={"tone": tone, "length": length, "goals": goals.strip(), "company": co},
            output=out,
            tags=["strategy", tone, length, lang],
            meta={"company": co.get("name","N/A")},
        )
    except Exception as e:
        st.error(f"Error generating idea: {e}")

out = st.session_state.get("si_output", "")
if out:
    st.markdown("### Result")
    st.markdown(out)

    st.download_button(
        "Download (.txt)",
        data=out.encode("utf-8"),
        file_name="strategy_idea.txt",
        mime="text/plain",
    )
    st.download_button(
        "Download (.docx)",
        data=text_to_docx_bytes(out),
        file_name="strategy_idea.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    st.download_button(
        "Download (.pdf)",
        data=text_to_pdf_bytes(out),
        file_name="strategy_idea.pdf",
        mime="application/pdf",
    )
