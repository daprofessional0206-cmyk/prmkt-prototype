# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st

from shared.state import get_company, get_brand_rules
from shared.llm import llm_copy, is_openai_ready
from shared.history import add_history


st.set_page_config(page_title="Content Engine", page_icon="📰", layout="wide")
st.title("📰 Content Engine")
st.caption("Generate press releases, ads, landing pages, blogs, and social posts.")

co = get_company()
brand_rules = get_brand_rules()

col1, col2 = st.columns(2)
with col1:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad Copy", "Landing Page", "Blog Post", "Social Post"],
        index=0,
    )
with col2:
    tone = st.selectbox("Tone", ["Professional", "Neutral", "Playful", "Bold"], index=0)

col3, col4 = st.columns(2)
with col3:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=0)
with col4:
    lang = st.selectbox("Language", ["English"], index=0)

cta = st.text_input("Call to action (optional)", value="")
topic = st.text_input("Topic / Offer / Product", value="")
bullets = st.text_area("Key points (bullets, optional)", value="", height=100)

count = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1)
go = st.button("Generate A/B/C Variants", type="primary", use_container_width=True)

if go:
    if not is_openai_ready():
        st.error("OpenAI key not found. Set it in **Admin Settings → How to set the key**.")
        st.stop()

    # Build prompt once
    br = f"\nBrand rules to respect: {brand_rules}" if brand_rules else ""
    pts = f"\nKey points:\n{bullets}" if bullets.strip() else ""
    cta_line = f"\nClear CTA: {cta}" if cta.strip() else ""
    base_prompt = (
        f"Write {count} distinct {content_type} variant(s) in {lang}. "
        f"Company: {co.name} (Industry: {co.industry}, Size: {co.size}).\n"
        f"Topic/Offer: {topic}\n"
        f"Tone: {tone}. Length: {length}.{br}{pts}{cta_line}\n"
        f"Format each variant with a short **headline** and a concise **body**.\n"
        f"Return plain text."
    )

    try:
        text = llm_copy(base_prompt)
        st.success("Draft(s) created!")
        st.text_area("Output", value=text, height=350)

        add_history(
            "variants",
            payload={
                "content_type": content_type,
                "tone": tone,
                "length": length,
                "language": lang,
                "topic": topic,
                "cta": cta,
                "bullets": bullets,
                "brand_rules_present": bool(brand_rules),
                "company": co.asdict(),
            },
            output={"text": text},
            tags=[content_type, lang, tone],
        )
    except Exception as e:
        st.error(
            "Couldn’t generate content. If you just rotated keys, hit **Manage app → Reboot**, "
            "then try again. Details were saved to history."
        )
        fallback = (
            "Draft:\n"
            "• Opening line tailored to the audience.\n"
            "• Benefit/feature #1\n"
            "• Benefit/feature #2\n"
            "• Clear CTA"
        )
        st.text_area("Fallback", value=fallback, height=220)
        add_history(
            "variants",
            payload={
                "content_type": content_type,
                "tone": tone,
                "length": length,
                "language": lang,
                "topic": topic,
                "cta": cta,
                "bullets": bullets,
                "brand_rules_present": bool(brand_rules),
                "company": co.asdict(),
            },
            output={"text": fallback, "error": str(e)},
            tags=[content_type, "fallback"],
        )
