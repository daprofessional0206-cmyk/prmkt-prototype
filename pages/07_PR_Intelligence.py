# pages/07_PR_Intelligence.py
from __future__ import annotations
import streamlit as st
from shared import state, llm, history

st.set_page_config(page_title="PR Intelligence", page_icon="📣", layout="wide")
st.title("📣 PR Intelligence (v1)")
st.caption("Get press-worthy story angles, target beats, timing windows, and one-line pitches.")

state.init()
co = state.get_company()

timing = st.selectbox("Timing preference", ["ASAP (next 7 days)", "Soon (2–4 weeks)", "This quarter", "No specific timing"], index=1)

if "pri_output" not in st.session_state:
    st.session_state["pri_output"] = ""

c1, c2 = st.columns([1,1])
with c1:
    if st.button("Generate PR Insights", use_container_width=True):
        prompt = f"""You are an elite PR strategist.
Company: {co.get('name','')} | Industry: {co.get('industry','')} | Audience: {co.get('audience','')}
Brand voice: {co.get('brand_voice','')} | Timing: {timing}

Deliver:
- 3 press-worthy story angles (headline + 2 lines)
- Suggested journalist beats/outlets
- Ideal timing windows
- One-line pitch for each.
"""
        try:
            out = llm.llm_copy(prompt)
            st.session_state["pri_output"] = out
            history.add(
                tool="PR Intelligence",
                payload={"timing": timing, "company": co},
                output=out,
                tags=["pr-intel", timing],
                meta={"company": co.get("name","N/A")},
            )
        except Exception as e:
            st.error(e)
with c2:
    if st.button("Clear Output", use_container_width=True):
        st.session_state["pri_output"] = ""

if st.session_state["pri_output"]:
    st.markdown(st.session_state["pri_output"])
