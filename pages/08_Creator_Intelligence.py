# pages/07_Creator_Intelligence.py — Creator Intelligence v1 (safe scaffolding)

from __future__ import annotations
import streamlit as st

# Soft imports
try:
    from shared import state, history, llm
except Exception:
    state = None  # type: ignore
    history = None  # type: ignore
    from shared import llm  # type: ignore

st.set_page_config(page_title="Creator Intelligence — Presence", page_icon="🎬", layout="wide")

st.title("🎬 Creator Intelligence (v1)")
st.caption("Hook ideas, formats, and visual beats for creators. (Scaffold)")

co = None
if state and hasattr(state, "get_company"):
    co = state.get_company()
else:
    co = type("Company", (), {"name": "Acme Innovations", "industry": "Technology", "size": "Mid-market", "goals": ""})()

platform = st.selectbox("Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "LinkedIn Video"], index=0)
niche = st.text_input("Niche / theme", value=f"{co.industry} buyers, decision-makers")
cta = st.text_input("Desired action (CTA)", value="Book a demo")
count = st.slider("How many hooks?", min_value=5, max_value=20, value=10, step=1)

col_a, col_b = st.columns([1, 1])
with col_a:
    run = st.button("Generate Hook Ideas", type="primary", use_container_width=True)
with col_b:
    clear = st.button("Clear Output", use_container_width=True)

if clear:
    st.session_state.pop("creator_hooks", None)
    st.rerun()

if run:
    prompt = f"""
You are a top content strategist for creators. Generate {count} hook ideas for {platform}.
Company: {co.name} (industry: {co.industry}, size: {co.size}).
Niche/theme: {niche}. Desired viewer action: {cta}.

For each hook include:
- Hook line (first 2–5 seconds),
- Format suggestion (talking head / b-roll / screen demo),
- Visual beat (text overlay / cutaway idea),
- Ending CTA line (short).

Return a numbered Markdown list only.
""".strip()

    try:
        if llm.online():
            out = llm.generate(prompt, temperature=0.7, max_tokens=1000)
        else:
            out = "\n".join([f"{i+1}. Hook idea #{i+1} — talking head, text overlay, ends with “{cta}”." for i in range(count)])

        st.session_state["creator_hooks"] = out

        # Save to history when available
        if history and hasattr(history, "add_history"):
            history.add_history(
                kind="creator_intel",
                payload={"platform": platform, "niche": niche, "cta": cta, "company": getattr(co, "__dict__", {})},
                output=out,
                tags=["intel", "creator", platform, co.industry],
            )
        st.success("Hook ideas generated.")
    except Exception as e:
        st.error(str(e))

if "creator_hooks" in st.session_state:
    st.markdown(st.session_state["creator_hooks"])
    st.download_button(
        "Download hooks (.md)",
        data=st.session_state["creator_hooks"].encode("utf-8"),
        file_name="creator_hooks.md",
        mime="text/markdown",
    )
