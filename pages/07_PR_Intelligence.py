# pages/06_PR_Intelligence.py — PR Intelligence v1 (safe scaffolding)

from __future__ import annotations
import streamlit as st

# Soft imports so the page never crashes if helpers are missing
try:
    from shared import state, history, llm
except Exception:
    state = None  # type: ignore
    history = None  # type: ignore
    from shared import llm  # type: ignore

st.set_page_config(page_title="PR Intelligence — Presence", page_icon="🧭", layout="wide")

st.title("🧭 PR Intelligence (v1)")
st.caption("Early intelligence layer: media angles, journalist beats, timing windows. (Scaffold)")

with st.expander("What is this?", expanded=False):
    st.write(
        "This module suggests PR story angles and timing windows for your industry. "
        "Today it runs on the LLM + your Company Profile. Later we’ll add real data sources (news feeds, journalist DBs)."
    )

# Read company safely
co = None
if state and hasattr(state, "get_company"):
    co = state.get_company()
else:
    co = type("Company", (), {"name": "Acme Innovations", "industry": "Technology", "size": "Mid-market", "goals": ""})()

topic = st.text_input("Focus topic (product / launch / announcement)", value="Launch of RoboHub 2.0")
market = st.text_input("Target market / region", value="US + EU")
timing = st.selectbox("Timing preference", ["Soon (2–4 weeks)", "Quarterly window", "Event-aligned"], index=0)

col_a, col_b = st.columns([1, 1])
with col_a:
    run = st.button("Generate PR Insights", type="primary", use_container_width=True)
with col_b:
    clear = st.button("Clear Output", use_container_width=True)

if clear:
    st.session_state.pop("pr_intel_output", None)
    st.rerun()

if run:
    base_prompt = f"""
You are a senior PR strategist. For the company {co.name} (industry: {co.industry}, size: {co.size}),
propose three press-worthy story angles for: "{topic}".

Also include:
- Suggested journalist beats (who would care),
- Ideal timing windows (consider '{timing}' and market '{market}'),
- One-line pitch per angle (compelling, specific, ethical).

Return a clean Markdown list with clear section headers. Do not add meta commentary.
""".strip()

    try:
        if llm.online():
            txt = llm.generate(base_prompt, temperature=0.6, max_tokens=900)
        else:
            txt = (
                "### Angles\n"
                "1) Automation & Workforce Uplift — how RoboHub 2.0 augments teams.\n"
                "2) Security & Compliance — SOC2 journey for mid-market.\n"
                "3) Speed-to-Value — case study style narrative.\n\n"
                "### Beats\n- Enterprise Tech\n- Supply Chain\n- Future of Work\n\n"
                "### Timing\n- 2–4 weeks (align with industry webinar)\n\n"
                "### Pitches\n- “How mid-market firms adopt robotics without disruption...”"
            )

        st.session_state["pr_intel_output"] = txt

        # Save to history if helper exists
        if history and hasattr(history, "add_history"):
            history.add_history(
                kind="pr_intel",
                payload={"topic": topic, "market": market, "timing": timing, "company": getattr(co, "__dict__", {})},
                output=txt,
                tags=["intel", "pr", co.industry, co.size],
            )
        st.success("PR insights generated.")
    except Exception as e:
        st.error(str(e))

if "pr_intel_output" in st.session_state:
    st.markdown(st.session_state["pr_intel_output"])
    st.download_button(
        "Download insights (.md)",
        data=st.session_state["pr_intel_output"].encode("utf-8"),
        file_name="pr_intelligence.md",
        mime="text/markdown",
    )
