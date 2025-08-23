# pages/02_Strategy_Ideas.py
from __future__ import annotations

import streamlit as st
from datetime import datetime

# Optional shared modules (safe fallbacks provided)
try:
    from shared.llm import llm_copy
except Exception:
    llm_copy = None

try:
    from shared.history import add_history
except Exception:
    def add_history(kind: str, payload: dict, output: str, tags: list[str] | None = None):
        rec = {"ts": datetime.utcnow().isoformat(timespec="seconds"), "kind": kind, "input": payload, "output": output}
        if tags:
            rec["tags"] = tags
        st.session_state.setdefault("history", [])
        st.session_state["history"].insert(0, rec)
        st.session_state["history"] = st.session_state["history"][:50]

try:
    from shared.state import get_company
except Exception:
    def get_company():
        return {
            "name": st.session_state.get("cp_name", "Acme Innovations"),
            "industry": st.session_state.get("cp_industry", "Technology"),
            "size": st.session_state.get("cp_size", "Mid-market"),
            "goals": st.session_state.get("cp_goals", ""),
        }

from shared.exports import text_to_docx_bytes, text_to_pdf_bytes


st.set_page_config(page_title="Presence — Strategy Ideas", page_icon="💡", layout="wide")

st.title("💡 Strategy Ideas")
st.caption("Brainstorm bold PR & marketing angles quickly, then export as .docx / .pdf.")

st.divider()

co = get_company()
goals = st.text_area(
    "Business Goals (auto-filled from Company Profile; adjust if needed)",
    value=co.get("goals", ""),
    height=90,
)

tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Visionary"], index=0)
length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

if st.button("Generate Strategy Idea", type="primary", use_container_width=True, key="btn_idea"):
    base_prompt = f"""
Propose a practical PR/Marketing initiative for {co['name']} ({co['industry']}, size: {co['size']}).
Goals: {goals or "(not specified)"}.
Output a brief, 4–6 bullet plan with headline, rationale, primary channel, and success metrics.
Match tone: {tone}. Length: {length}.
""".strip()

    with st.spinner("Thinking..."):
        try:
            if llm_copy is not None and st.secrets.get("OPENAI_API_KEY"):
                idea = llm_copy(base_prompt, temperature=0.55, max_tokens=400)
            else:
                idea = f"""**Campaign Idea: “Momentum Now”**
- **Rationale:** Convert in-market demand with fast, helpful education.
- **Primary channel:** Organic social + email drips; PR angle for thought-leadership.
- **Tactics:** Rapid Q&A posts, 2 customer mini-stories, founder AMAs, and one simple ROI calculator.
- **Measurement:** CTR to calculator, demo requests, and 30-day retention of new leads.
- **Notes:** Align tone to {co['size'].lower()} buyers in {co['industry'].lower()}."""
        except Exception as e:
            st.error(f"LLM error: {e}")
            idea = """**Campaign Idea: “Momentum Now”**
- Backup idea generated offline template."""

    st.success("Strategy idea created.")
    st.markdown(idea)

    # downloads
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download Idea (.docx)",
            data=text_to_docx_bytes("Strategy Idea", idea),
            file_name="strategy_idea.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    with c2:
        st.download_button(
            "Download Idea (.pdf)",
            data=text_to_pdf_bytes("Strategy Idea", idea),
            file_name="strategy_idea.pdf",
            mime="application/pdf",
        )

    # history record
    add_history(
        "Strategy",
        payload={"tone": tone, "length": length, "goals": (goals or "").strip(), "company": co},
        output=idea,
        tags=["strategy", tone, length],
    )
