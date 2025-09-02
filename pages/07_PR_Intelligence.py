# pages/07_PR_Intelligence.py
from __future__ import annotations
import streamlit as st
from shared import state, history
from shared.llm import llm_copy
from shared.exports import text_to_pdf_bytes, text_to_docx_bytes

st.set_page_config(page_title="PR Intelligence", page_icon="📣", layout="wide")
st.title("📣 PR Intelligence (v1)")
st.caption("Get press-worthy story angles, target beats, timing windows, and one-line pitches.")

state.init()
co = state.get_company()  # dict or simple obj

timing = st.selectbox(
    "Timing preference",
    ["ASAP (next 7 days)", "Soon (2–4 weeks)", "This quarter", "No specific timing"],
)

# Present context
company = co.get("name", "") if isinstance(co, dict) else getattr(co, "name", "")
industry = co.get("industry", "") if isinstance(co, dict) else getattr(co, "industry", "")
audience = co.get("audience", "") if isinstance(co, dict) else getattr(co, "audience", "")
st.write(f"**Context** — Company: {company} | Industry: {industry} | Audience: {audience}")

colA, colB = st.columns([1,1])
run = colA.button("Generate PR Insights", use_container_width=True)
clear = colB.button("Clear Output", use_container_width=True)

if clear:
    st.experimental_rerun()

if run:
    prompt = f"""
Act as a PR strategist. Using the context below, propose 3–5 press-worthy story angles,
recommended journalist beats, suggested timing windows ({timing}), and a one-line pitch for each.

Context:
- Company: {company}
- Industry: {industry}
- Audience: {audience}
    """.strip()

    with st.spinner("Thinking like a PR desk…"):
        try:
            out = llm_copy(prompt)
        except Exception:
            out = "Could not generate insights right now. Try again."

    st.markdown(out)

    # Exports
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download (.docx)",
            data=text_to_docx_bytes(out, title="PR Intelligence"),
            file_name="pr_intelligence.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "Download (.pdf)",
            data=text_to_pdf_bytes(out, title="PR Intelligence"),
            file_name="pr_intelligence.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # History
    try:
        history.add(
            kind="pr_intel",
            title=f"PR Insights — {timing}",
            payload={"insights": out},
            meta={"company": company, "timing": timing},
            tags=["pr", "intel", timing],
        )
    except Exception:
        pass
