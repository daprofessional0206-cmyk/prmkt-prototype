# pages/02_Strategy_Ideas.py
from __future__ import annotations

import streamlit as st
from dataclasses import asdict

from shared.state import get_company
from shared.history import add
from shared.llm import llm_copy, is_openai_ready

st.title("Strategy Ideas")

co = get_company()
# normalize company to a dict
if hasattr(co, "__dict__"):
    company = asdict(co)
elif isinstance(co, dict):
    company = co
else:
    company = {"name": str(co), "industry": "", "size": "", "goals": ""}

st.caption("Generate a quick, practical PR/Marketing initiative.")

if st.button("Generate Strategy Idea", use_container_width=True):
    prompt = f"""
Propose a practical PR/Marketing initiative for {company.get('name','(company)')}
(industry: {company.get('industry','')}, size: {company.get('size','')}).

Business goals: {company.get('goals','(not specified)')}.

Output a brief, 4–6 bullet plan with:
- Campaign headline
- Rationale
- Primary channel(s)
- 3–4 key tactics
- Success metrics
""".strip()

    try:
        if not is_openai_ready():
            raise RuntimeError("OpenAI is not configured")

        idea = llm_copy(prompt, temperature=0.5, max_tokens=350)
        st.success("Strategy idea created.")
        st.markdown(idea)

        add(
            kind="strategy",
            payload=company,
            output=idea,
            tags=["strategy", company.get("industry", "")]
        )

    except Exception as e:
        fallback = f"""**Campaign Idea (offline template)**  
- **Rationale:** Convert in-market demand with clear, helpful education.  
- **Primary channel:** Organic social + email; PR angle for thought-leadership.  
- **Tactics:** Rapid Q&A posts, 2 customer mini-stories, founder AMA, simple ROI calc.  
- **Measurement:** CTR to calculator, demo requests, 30-day lead retention.

_(Fallback used due to LLM error: {e!s})_
"""
        st.info("Generated an offline template (LLM unavailable).")
        st.markdown(fallback)

        add(
            kind="strategy",
            payload=company,
            output=fallback,
            tags=["strategy", "offline"]
        )
