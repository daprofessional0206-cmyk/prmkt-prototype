from __future__ import annotations

import streamlit as st
from dataclasses import asdict
from shared import state, llm
from shared.history import add_history

st.set_page_config(page_title="PR Intelligence", page_icon="📣", layout="wide")
st.title("📣 PR Intelligence (v1)")
st.caption("Get press-worthy story angles, target beats, timing windows, and one-line pitches.")

state.init()
co = state.get_company()  # our Company dataclass or dict-like

# --- Inputs -------------------------------------------------------------------
timing = st.selectbox(
    "Timing preference",
    ["ASAP (next 7 days)", "Soon (2–4 weeks)", "This quarter", "No specific timing"],
    index=1,
)

col_a, col_b = st.columns([1, 1])
with col_a:
    do = st.button("Generate PR Insights", type="primary")
with col_b:
    if st.button("Clear Output"):
        st.session_state.pop("pr_intel_md", None)
        st.rerun()

# --- Generate -----------------------------------------------------------------
if do:
    system = (
        "You are a senior PR strategist. Return crisp, press-worthy recommendations. "
        "Use clear markdown with headings and bullet points."
    )
    prompt = f"""
Company:
- Name: {co.name if hasattr(co, "name") else co.get("name","")}
- Industry: {co.industry if hasattr(co, "industry") else co.get("industry","")}
- Size: {co.size if hasattr(co, "size") else co.get("size","")}
- Audience: {co.audience if hasattr(co, "audience") else co.get("audience","")}
- Goals: {co.goals if hasattr(co, "goals") else co.get("goals","")}
- Brand rules (if any): {state.get_brand_rules().strip()}

Timing preference: {timing}

Return:
1) **3 story angles** with a short explanation for each.
2) Suggested **journalist beats** to target.
3) Recommended **timing windows** (why that window).
4) A **one-line pitch** per angle (email subject quality).
"""
    try:
        md = llm.llm_copy(system=system, prompt=prompt, temperature=0.3)
    except Exception as e:
        md = f"**Fallback:** could not reach LLM.\n\nError: `{e}`"

    st.session_state["pr_intel_md"] = md

    # ✅ write to history (content, not output)
    meta = {
        "timing": timing,
        "company": asdict(co) if hasattr(co, "__dict__") else dict(co),
    }
    add_history("pr_intel", meta, md, tags=["pr", "intelligence", timing])

# --- Output -------------------------------------------------------------------
st.markdown(st.session_state.get("pr_intel_md", ""), unsafe_allow_html=False)
