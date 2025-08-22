from __future__ import annotations

import streamlit as st
from dataclasses import asdict
from shared import state, llm
from shared.history import add_history

st.set_page_config(page_title="Creator Intelligence", page_icon="🎬", layout="wide")
st.title("🎬 Creator Intelligence (v1)")
st.caption("Generate high-signal hook ideas with format + visual guidance, tailored to your audience.")

state.init()
co = state.get_company()

# --- Inputs -------------------------------------------------------------------
platform = st.selectbox(
    "Platform",
    ["Instagram Reels", "YouTube Shorts", "TikTok", "LinkedIn Video", "Twitter/X"],
    index=0,
)
niche = st.text_input("Niche / theme", placeholder="buyers, decision-makers")
cta = st.text_input("Desired action (CTA)", placeholder="Book a demo")
k = st.slider("How many hooks?", value=10, min_value=5, max_value=20, step=1)

col_a, col_b = st.columns([1, 1])
with col_a:
    do = st.button("Generate Hook Ideas", type="primary")
with col_b:
    if st.button("Clear Output"):
        st.session_state.pop("creator_hooks_md", None)
        st.rerun()

# --- Generate -----------------------------------------------------------------
if do:
    system = (
        "You are a social video creative director. Produce concise, scroll-stopping hooks. "
        "For each hook, include: Hook Line, Format Suggestion, Visual Beat, Ending CTA Line. "
        "Keep each item tight (1–2 sentences per field)."
    )
    prompt = f"""
Company:
- Name: {co.name if hasattr(co, "name") else co.get("name","")}
- Industry: {co.industry if hasattr(co, "industry") else co.get("industry","")}
- Audience: {co.audience if hasattr(co, "audience") else co.get("audience","")}
- Brand rules (if any): {state.get_brand_rules().strip()}

Platform: {platform}
Niche/theme: {niche}
Target action: {cta}
Count: {k}

Return a numbered list. For each item show:
- Hook Line:
- Format Suggestion:
- Visual Beat:
- Ending CTA Line:
"""
    try:
        md = llm.llm_copy(system=system, prompt=prompt, temperature=0.6)
    except Exception as e:
        md = f"**Fallback:** could not reach LLM.\n\nError: `{e}`"

    st.session_state["creator_hooks_md"] = md

    # ✅ write to history (content, not output)
    meta = {
        "platform": platform,
        "niche": niche,
        "cta": cta,
        "count": k,
        "company": asdict(co) if hasattr(co, "__dict__") else dict(co),
    }
    add_history("creator_hooks", meta, md, tags=["creator", platform, "hooks"])

# --- Output -------------------------------------------------------------------
st.markdown(st.session_state.get("creator_hooks_md", ""), unsafe_allow_html=False)
