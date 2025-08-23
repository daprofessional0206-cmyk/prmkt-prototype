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


st.set_page_config(page_title="Creator Intelligence", page_icon="🎬", layout="wide")
st.title("🎬 Creator Intelligence (v1)")
st.caption("Generate high-performing hooks with visual beats and CTA lines for short-form video.")

state.init()
co = state.get_company()

# --- Controls ---------------------------------------------------------------
platform = st.selectbox(
    "Platform",
    ["Instagram Reels", "TikTok", "YouTube Shorts", "LinkedIn Video"],
)
theme = st.text_input("Niche / theme", value=co_get(co, "audience", "buyers, decision-makers"))
cta = st.text_input("Desired action (CTA)", value="Book a demo")
count = st.slider("How many hooks?", 3, 15, 8)

c1, c2 = st.columns([1, 1])
with c1:
    do = st.button("Generate Hook Ideas", type="primary")
with c2:
    if st.button("Clear Output"):
        st.session_state.pop("creator_hooks_md", None)
        st.rerun()

# --- Context + prompt -------------------------------------------------------
context = f"""
Company: {co_get(co, "name")}
Industry: {co_get(co, "industry")}
Audience: {co_get(co, "audience")}
Tone/rules: {co_get(co, "brand_rules")}
Goal: {co_get(co, "goals")}
"""

prompt = f"""
You are a senior short-form video coach for {platform}.

Create {count} **high-performing hook ideas** for the niche/theme "{theme}" that drive viewers to **{cta}**.
For each item, include:
- **Hook line** (7–12 words, punchy)
- **Format suggestion** (e.g., talking head, b-roll + captions, split-screen, POV)
- **Visual beat** (what appears on screen in first 3 seconds)
- **Ending CTA line** (restate desired action)

Keep it on-brand using the rules and audience in the context.
Return polished markdown as a numbered list.

Context:
{context}
""".strip()

# --- Run --------------------------------------------------------------------
if do:
    try:
        result = llm_copy(prompt, temperature=0.8, max_tokens=1000)
        md = result.strip() if result else "_No output._"
    except Exception as e:
        md = f"**Fallback (LLM error):** {e}\n\n1. Hook Line: Example\n   Format: Talking head\n   Visual Beat: Text overlay\n   Ending CTA: {cta}"

    st.session_state["creator_hooks_md"] = md
    add_history(
        "creator_hooks",
        {"platform": platform, "theme": theme, "cta": cta, "count": count},
        md,
        tags=["creator_hooks", platform],
    )

st.markdown(st.session_state.get("creator_hooks_md", ""))
