# pages/08_Creator_Intelligence.py
from __future__ import annotations
import streamlit as st
from shared import state, history
from shared.llm import llm_copy
from shared.exports import text_to_pdf_bytes, text_to_docx_bytes

st.set_page_config(page_title="Creator Intelligence", page_icon="🎬", layout="wide")
st.title("🎬 Creator Intelligence")

state.init()
co = state.get_company()

platform = st.selectbox(
    "Platform",
    ["Instagram Reels", "YouTube Shorts", "TikTok", "LinkedIn Video", "Twitter/X"],
)
niche = st.text_input("Niche / theme", value=(co.get("audience", "") if isinstance(co, dict) else getattr(co, "audience", "")))
cta = st.text_input("Desired action (CTA)", value="Book a demo")
n_hooks = st.slider("How many hooks?", 5, 20, 10)

colA, colB = st.columns([1,1])
run = colA.button("Generate Hook Ideas", use_container_width=True)
clear = colB.button("Clear Output", use_container_width=True)

if clear:
    st.experimental_rerun()

if run:
    prompt = f"""
You are a social content strategist.
Generate {n_hooks} high-performing short-video hooks for {platform} in the niche "{niche}".
Each hook should include:
- Hook line
- Suggested format (e.g., talking head, street vox-pop, B-roll with captions)
- Visual beat (what appears on screen)
- Ending CTA line (target CTA: {cta})
Return numbered items.
    """.strip()

    with st.spinner("Brainstorming scroll-stoppers…"):
        try:
            out = llm_copy(prompt)
        except Exception:
            out = "Could not generate hooks right now."

    st.markdown(out)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download (.docx)",
            data=text_to_docx_bytes(out, title="Creator Intelligence — Hooks"),
            file_name="creator_intelligence_hooks.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "Download (.pdf)",
            data=text_to_pdf_bytes(out, title="Creator Intelligence — Hooks"),
            file_name="creator_intelligence_hooks.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    try:
        history.add(
            kind="creator",
            title=f"{platform} hooks x{n_hooks}",
            payload={"hooks": out},
            meta={"platform": platform, "niche": niche, "cta": cta},
            tags=["creator", platform.lower(), niche],
        )
    except Exception:
        pass
