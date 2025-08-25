# pages/08_Creator_Intelligence.py
from __future__ import annotations
import streamlit as st
from shared import state, llm, history

st.set_page_config(page_title="Creator Intelligence", page_icon="🎥", layout="wide")
st.title("🎥 Creator Intelligence (v1)")
st.caption("Hook ideas + beats for short-form videos.")

state.init()
co = state.get_company()

platform = st.selectbox("Platform", ["Instagram Reels", "TikTok", "YouTube Shorts"], index=0)
niche = st.text_input("Niche / theme", value=co.get("audience",""))
cta = st.text_input("Desired action (CTA)", value="Book a demo")
count = st.slider("How many hooks?", 3, 20, 10)

if "ci_output" not in st.session_state:
    st.session_state["ci_output"] = ""

c1, c2 = st.columns([1,1])
with c1:
    if st.button("Generate Hook Ideas", use_container_width=True):
        prompt = f"""You are a short-form content strategist for {platform}.
Company: {co.get('name','')} (industry: {co.get('industry','')}), audience: {niche}.
Generate {count} hook ideas. For each, give:
- Hook line
- Format suggestion (e.g., talking head, green screen, b-roll)
- Visual beat
- Ending CTA line: "{cta}"
Keep them concise and punchy."""
        try:
            out = llm.llm_copy(prompt)
            st.session_state["ci_output"] = out
            history.add(
                tool="Creator Intelligence",
                payload={"platform": platform, "niche": niche, "cta": cta, "count": count, "company": co},
                output=out,
                tags=["creator", platform],
                meta={"company": co.get("name","N/A")},
            )
        except Exception as e:
            st.error(e)
with c2:
    if st.button("Clear Output", use_container_width=True):
        st.session_state["ci_output"] = ""

if st.session_state["ci_output"]:
    st.markdown(st.session_state["ci_output"])
