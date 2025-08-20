# pages/02_Strategy_Ideas.py
from __future__ import annotations

import streamlit as st

from shared import state, ui
from shared.llm import llm_copy, is_openai_ready
from shared.history import add_history  # expects add_history(kind, input, output, tags)
from dataclasses import asdict  # safe to import even if we don't use it

st.set_page_config(page_title="Strategy Ideas", page_icon="💡", layout="wide")

ui.page_title("Strategy Ideas", "Brainstorm bold PR & marketing angles quickly.")

# ---------------------------------------------------------------------
# Read company as a DICT (this is important)
# ---------------------------------------------------------------------
co = state.get_company()  # returns dict like {"name": "...", "industry": "...", ...}

with st.form("strategy_form"):
    goals = st.text_area(
        "Business Goals (optional override)",
        placeholder="e.g., Increase brand awareness with mid-market B2B buyers, drive 200 qualified demo requests.",
        height=120,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        tone = st.selectbox("Tone", ["Professional", "Bold", "Playful", "Journalistic"])
    with col2:
        length = st.selectbox("Length", ["Short", "Medium", "Long"])

    submitted = st.form_submit_button("✨ Generate Strategy Idea", use_container_width=True)

if submitted:
    if not is_openai_ready():
        st.error("Could not generate right now. LLM may be rate-limited or the key is invalid. Check **Admin Settings → OpenAI** and try again.")
    else:
        # Build the prompt using dict-safe access
        name = co.get("name", "Company")
        industry = co.get("industry", "Industry")
        size = co.get("size", "Mid-market")
        goals_text = (goals or co.get("goals", "") or "").strip()

        prompt = f"""You are a senior PR/Marketing strategist.

Company: {name} (Industry: {industry}, Size: {size})
Business goals: {goals_text or "(not specified)"}

Write ONE practical, high‑leverage PR/marketing initiative tailored to this profile.
Constraints:
- Tone: {tone}
- Length: {length}
- Keep it realistic and immediately actionable
- Include a 1‑line Objective, the Core Idea, 3–5 Execution Steps, and a Success metric
"""

        # Call LLM with a tiny wrapper
        output_text = None
        err_msg = None
        try:
            output_text = llm_copy(prompt, max_tokens=500)
        except Exception as e:
            err_msg = str(e)

        if output_text:
            st.success("Idea generated!")
            st.markdown(output_text)

            # Always write history with input & output keys
            add_history(
                "strategy",
                input={"prompt": prompt, "tone": tone, "length": length, "goals": goals_text, "company": co},
                output={"text": output_text},
                tags=["strategy", tone, length, industry, size],
            )
        else:
            st.error("Could not generate right now. LLM may be rate-limited or the key is invalid. Check **Admin Settings → OpenAI** and try again.")
            # Fallback idea so the page is never blank
            fallback = f"""**Objective:** Raise awareness among {size} buyers in {industry} this quarter.

**Core Idea:** Publish a monthly “{industry} Cost‑Saver” benchmark — short, visual, and quotable.

**Execution Steps**
1) Analyze anonymized client data + public sources to extract 3 cost or time benchmarks.
2) Design a snackable 1‑pager + 3 social posts; pitch the stat to niche reporters/newsletters.
3) Host a 20‑min live breakdown with your Head of {industry} on LinkedIn.
4) Gate a detailed PDF for MQL capture.

**Metric:** 20 qualified inbound requests or 5 media placements in 30 days."""
            st.info("Fallback idea:")
            st.markdown(fallback)

            add_history(
                "strategy",
                input={"prompt": prompt, "tone": tone, "length": length, "goals": goals_text, "company": co},
                output={"text": fallback, "error": err_msg or "fallback"},
                tags=["strategy", "fallback", tone, length, industry, size],
            )
