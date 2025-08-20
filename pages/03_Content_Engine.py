# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st

from shared import state, ui
from shared.llm import llm_copy, is_openai_ready
from shared.history import add_history

st.set_page_config(page_title="Content Engine", page_icon="📝", layout="wide")

ui.page_title(
    "Content Engine",
    "Generate press releases, ads, posts, landing pages, and social content.",
)

# ------------------------- inputs ------------------------------------
co = state.get_company()  # dict
lang = st.selectbox("Language", ["English"], index=0)
variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1)

content_type = st.selectbox(
    "Content type",
    [
        "Press Release",
        "Ad Copy",
        "Landing Page",
        "LinkedIn Post",
        "Twitter/X Thread",
        "Email",
        "Blog Intro",
    ],
)

tone = st.selectbox("Tone", ["Professional", "Bold", "Playful", "Journalistic"], index=0)
length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

generate = st.button("Generate A/B/C Variants", use_container_width=True)

def make_prompt(content_type: str, company: dict, tone: str, length: str, lang: str) -> str:
    name = company.get("name", "Company")
    industry = company.get("industry", "Industry")
    size = company.get("size", "Mid-market")
    goals = (company.get("goals", "") or "").strip()
    rules = (state.get_brand_rules() or "").strip()

    return f"""You are a senior copywriter.

Company: {name} (Industry: {industry}, Size: {size}).
Goals: {goals or "(not specified)"}.
Brand rules (do/don't, banned words), if any:
{rules or "(none)"}

Write {variants} {content_type} variant(s) in {lang}.
Tone: {tone}. Length: {length}.

Each variant must be clearly separated with a heading like 'Variant 1', 'Variant 2', etc.
Include: a strong hook, 2–3 proof points tied to the audience, and a clear CTA.
Avoid generic filler; keep it brand‑safe."""
# ---------------------------------------------------------------------

if generate:
    if not is_openai_ready():
        st.error("LLM not ready. Check **Admin Settings → OpenAI** and try again.")
    else:
        p = make_prompt(content_type, co, tone, length, lang)
        txt = None
        err = None
        try:
            txt = llm_copy(p, max_tokens=900)
        except Exception as e:
            err = str(e)

        if txt:
            st.success("Draft(s) created!")
            st.markdown(txt)
            add_history(
                "variants",
                input={
                    "prompt": p,
                    "content_type": content_type,
                    "tone": tone,
                    "length": length,
                    "language": lang,
                    "company": co,
                },
                output={"text": txt},
                tags=["variants", content_type, tone, length, lang, co.get("industry", "Industry"), co.get("size", "Mid-market")],
            )
        else:
            st.error("Could not generate right now (LLM issue). Showing a minimal fallback draft.")
            fallback = "Draft:\n• Opening line tailored to the audience.\n• Benefit/feature #1\n• Benefit/feature #2\n• Clear CTA"
            st.code(fallback)
            add_history(
                "variants",
                input={
                    "prompt": p,
                    "content_type": content_type,
                    "tone": tone,
                    "length": length,
                    "language": lang,
                    "company": co,
                },
                output={"text": fallback, "error": err or "fallback"},
                tags=["variants", "fallback", content_type, tone, length, lang],
            )
