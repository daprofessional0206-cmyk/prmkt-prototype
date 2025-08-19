# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st
from dataclasses import asdict
from typing import List

from shared.state import get_company, get_brand_rules
from shared.history import add
from shared.llm import llm_copy, is_openai_ready

st.title("Content Engine — A/B/C")

# ---------- Inputs ----------
col1, col2 = st.columns([1, 1])
with col1:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad", "Social Post", "Landing Page", "Email"]
    )
    platform = st.selectbox(
        "Platform (for Social/Ad)",
        ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"]
    )
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0")
    bullets_raw = st.text_area(
        "Key Points (bullets, one per line)",
        value="2× faster setup\nSOC 2 Type II\nSave 30% cost",
        height=120,
    )

with col2:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"])
    length = st.selectbox("Length", ["Short", "Medium", "Long"])
    audience = st.text_input("Audience (who is this for?)", value="Decision-makers")
    cta = st.text_input("Call to Action", value="Book a demo")

st.subheader("Brand Rules (read-only)")
with st.expander("View current brand rules", expanded=False):
    st.code(get_brand_rules() or "(none)")

col_lang, col_var = st.columns([2, 1])
with col_lang:
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0)
with col_var:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1)

# ---------- Helpers ----------
def _norm_company() -> dict:
    co = get_company()
    if hasattr(co, "__dict__"):
        return asdict(co)
    if isinstance(co, dict):
        return co
    return {"name": str(co), "industry": "", "size": "", "goals": ""}

def _bulletize(text: str) -> List[str]:
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]

def _make_prompt(
    content_type: str,
    tone: str,
    length: str,
    platform: str,
    audience: str,
    cta: str,
    topic: str,
    bullets: List[str],
    language: str,
    variants: int,
    brand_rules: str,
    company: dict,
) -> str:
    bullets_md = "\n".join([f"- {b}" for b in bullets]) if bullets else "(no bullets provided)"
    rules = (brand_rules or "").strip() or "(none provided)"
    return f"""
Generate {variants} distinct variant(s) of a {length.lower()} {content_type.lower()}.

Language: {language}.
Audience: {audience}. Tone: {tone}.
Company: {company.get('name','(Company)')} ({company.get('industry','Industry')}, size: {company.get('size','')})
Platform: {platform}
Topic / Offer: {topic}

Key points:
{bullets_md}

Call to action: {cta}

Brand rules (follow & avoid banned words):
{rules}

Constraints:
- Brand-safe, factual from provided info only.
- Strong opening, clear structure, crisp CTA.
- If multiple variants are requested, make them clearly different.
""".strip()

def _offline_draft(content_type: str, tone: str, length: str, audience: str, bullets: List[str], cta: str, err: Exception | None) -> str:
    bullets_md = "\n".join([f"• {b}" for b in (bullets or ['Benefit/feature #1','Benefit/feature #2'])])
    note = f"\n\n_(Fallback used due to LLM error: {err!s})_" if err else ""
    return f"""Draft:
• Opening line tailored to the audience ({audience}).
{bullets_md}
• Clear CTA: {cta}{note}
"""

# ---------- Action ----------
if st.button("Generate A/B/C Variants", use_container_width=True):
    if not topic.strip():
        st.warning("Please add a Topic / Offer first.")
        st.stop()

    company = _norm_company()
    bullets = _bulletize(bullets_raw)
    brand_rules = get_brand_rules()

    prompt = _make_prompt(
        content_type=content_type,
        tone=tone,
        length=length,
        platform=platform,
        audience=audience or "Decision-makers",
        cta=cta or "Get started",
        topic=topic,
        bullets=bullets,
        language=language,
        variants=int(variants),
        brand_rules=brand_rules,
        company=company,
    )

    outputs: List[str] = []
    err: Exception | None = None

    try:
        if not is_openai_ready():
            raise RuntimeError("OpenAI is not configured")
        raw = llm_copy(prompt, temperature=0.65, max_tokens=1200)
        # let users separate variants with a blank line + -- (but also tolerate any blob)
        parts = [seg.strip() for seg in raw.split("\n\n--\n\n") if seg.strip()]
        if not parts:
            parts = [raw.strip()] if raw.strip() else []
        while len(parts) < int(variants) and parts:
            parts.append(parts[-1])
        outputs = parts[: int(variants)]
    except Exception as e:
        err = e
        outputs = [_offline_draft(content_type, tone, length, audience, bullets, cta, err)]

    # Render
    st.success("Draft(s) created!")
    for idx, draft in enumerate(outputs, start=1):
        st.markdown(f"### Variant {idx}")
        st.markdown(draft)
        st.download_button(
            label=f"Download Variant {idx} (.txt)",
            data=draft.encode("utf-8"),
            file_name=f"variant_{idx}_{content_type.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            key=f"dl_{idx}"
        )
        st.divider()

    # History
    add(
        kind="Variants",
        payload={
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "platform": platform,
            "audience": audience,
            "cta": cta,
            "topic": topic,
            "bullets": bullets,
            "language": language,
            "variants": int(variants),
            "brand_rules": (brand_rules or ""),
            "company": company,
            "used_llm": err is None,
        },
        output=outputs,
        tags=[content_type, language, platform]
    )
