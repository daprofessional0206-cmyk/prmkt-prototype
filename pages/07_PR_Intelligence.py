from __future__ import annotations

import streamlit as st
from shared import state
from shared.history import add_history
from shared.llm import llm_copy


def co_get(co, key: str, default: str = "") -> str:
    """Safe getter that works with either a dataclass-like object or a dict."""
    try:
        if isinstance(co, dict):
            return co.get(key, default)
        return getattr(co, key, default)
    except Exception:
        return default


st.set_page_config(page_title="PR Intelligence", page_icon="📣", layout="wide")
st.title("📣 PR Intelligence (v1)")
st.caption("Get press-worthy story angles, target beats, timing windows, and one-line pitches.")

state.init()
co = state.get_company()

# --- Controls ---------------------------------------------------------------
timing = st.selectbox(
    "Timing preference",
    ["ASAP (next 7 days)", "Soon (2–4 weeks)", "This quarter", "No specific timing"],
    index=1,
)

c1, c2 = st.columns([1, 1])
with c1:
    do = st.button("Generate PR Insights", type="primary")
with c2:
    if st.button("Clear Output"):
        st.session_state.pop("pr_intel_md", None)
        st.rerun()

# --- Build company context safely ------------------------------------------
context = f"""
Company: {co_get(co, "name")}
Industry: {co_get(co, "industry")}
Size: {co_get(co, "size")}
Audience: {co_get(co, "audience")}
Competitors: {co_get(co, "competitors")}
Goals: {co_get(co, "goals")}
Brand rules / voice: {co_get(co, "brand_rules")}
"""

# --- Prompt -----------------------------------------------------------------
prompt = f"""
You are a senior PR strategist.

Given the company context and timing preference, propose 4–6 **press-worthy story angles** with:
- Suggested **journalist beats** to target
- Ideal **timing windows** (based on "{timing}")
- A sharp **one-line pitch** for each angle

Return clear, skimmable markdown.

Company context:
{context}
""".strip()

# --- Run --------------------------------------------------------------------
if do:
    try:
        result = llm_copy(prompt, temperature=0.7, max_tokens=900)
        md = result.strip() if result else "_No output._"
    except Exception as e:
        md = f"**Fallback (LLM error):** {e}\n\n- Angle A\n- Angle B\n- Angle C"

    st.session_state["pr_intel_md"] = md
    add_history(
        "pr_intel",
        {"timing": timing, "company": co_get(co, "name")},
        md,
        tags=["pr_intel", timing],
    )

st.markdown(st.session_state.get("pr_intel_md", ""))
