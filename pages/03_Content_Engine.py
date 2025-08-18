# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st
from datetime import datetime
from typing import List

# Internal helpers (existing modules in your repo)
from shared.state import get_company, get_brand_rules
from shared.history import add as add_history
# LLM gateway: we import safely; if unavailable, we'll fall back to offline
try:
    from shared.llm import generate as llm_generate, is_online as llm_is_online
except Exception:
    llm_generate = None
    llm_is_online = lambda: False  # noqa: E731


# ─────────────────────────────────────────────────────────────
# Small local utils (kept here to avoid extra imports)
# ─────────────────────────────────────────────────────────────
def bulletize(text: str) -> List[str]:
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]


def make_prompt(
    *,
    content_type: str,
    platform: str,
    topic: str,
    bullets: List[str],
    tone: str,
    length: str,
    audience: str,
    cta: str,
    language: str,
    variants: int,
    brand_rules: str,
    company: dict,
) -> str:
    bullets_md = "\n".join([f"- {b}" for b in bullets]) if bullets else "(no bullets provided)"
    rules = brand_rules.strip() or "(none provided)"
    return f"""
Generate {variants} distinct variant(s) of a {length.lower()} {content_type.lower()} for platform "{platform}".

Language: {language}
Audience: {audience}
Tone: {tone}

Company: {company.get('name','(Company)')} ({company.get('industry','Industry')}, size: {company.get('size','Size')})
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
Return ONLY the copy. Separate each variant with a line containing: -- on its own line.
""".strip()


def offline_fallback(
    *,
    content_type: str,
    topic: str,
    bullets: List[str],
    tone: str,
    length: str,
    audience: str,
    cta: str,
    language: str,
    variants: int,
    company: dict,
) -> List[str]:
    """Simple local generator used when no API key is configured."""
    bullets_md = "\n".join([f"• {b}" for b in bullets]) if bullets else "• Add 2–3 benefits your buyer cares about."
    opening = {
        "Ad": "Attention, innovators!",
        "Social Post": "Quick update:",
        "Landing Page": "Welcome — here’s how we help:",
        "Email": "Hi there,",
        "Press Release": "FOR IMMEDIATE RELEASE",
    }.get(content_type, "Here’s something useful:")

    base = f"""{opening}

{company.get('name','Your brand')} presents **{topic}** for {audience.lower() if audience else 'your audience'}.
Tone: {tone}. Length: {length.lower()}. Language: {language}.

What you’ll get:
{bullets_md}

Next step: **{cta or 'Get started today.'}**
"""
    # create N lightly varied variants
    outs = []
    for i in range(variants):
        suffix = "" if i == 0 else f"\n\n(Perspective {i+1}: tweaks in phrasing and emphasis.)"
        outs.append(base + suffix)
    return outs


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────
st.title("🧠 Content Engine — AI Copy (A/B/C)")
st.caption("Create on-brand copy for PR/marketing. Supports brand rules, languages, and up to 3 variants.")
st.divider()

company = get_company()  # dict with name/industry/size/goals
brand_rules = get_brand_rules()  # string (may be "")

left, right = st.columns([1, 1], vertical_alignment="top")

with left:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad", "Social Post", "Landing Page", "Email"],
        key="ce_type",
    )
    platform = st.selectbox(
        "Platform (for Social/Ad)",
        ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"],
        key="ce_platform",
    )
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0", key="ce_topic")
    bullets_raw = st.text_area(
        "Key Points (bullets, one per line)",
        value="2× faster setup\nSOC 2 Type II\nSave 30% cost",
        height=120,
        key="ce_bullets",
    )

with right:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"], key="ce_tone")
    length = st.selectbox("Length", ["Short", "Medium", "Long"], key="ce_length")
    audience = st.text_input("Audience (who is this for?)", value="Decision-makers", key="ce_audience")
    cta = st.text_input("Call to Action", value="Book a demo", key="ce_cta")

st.subheader("Brand Rules (read-only)")
st.caption("Edit brand rules on the Company Profile page. These rules are applied here automatically.")
with st.expander("View current brand rules", expanded=False):
    st.code(brand_rules or "(none)", language="markdown")

col_lang, col_var = st.columns([2, 1])
with col_lang:
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0, key="ce_language")
with col_var:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1, key="ce_variants")

bullets = bulletize(bullets_raw)

# Hints (non-blocking)
issues = []
if not topic.strip():
    issues.append("Add a topic / product name.")
if len(bullets) == 0:
    issues.append("Add at least one bullet point (one per line).")
if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

# Generate
if st.button("Generate A/B/C Variants", key="btn_generate_variants", use_container_width=True):
    if not topic.strip() or len(bullets) == 0:
        st.warning("Please fill Topic and at least one bullet point.")
        st.stop()

    prompt = make_prompt(
        content_type=content_type,
        platform=platform,
        topic=topic,
        bullets=bullets,
        tone=tone,
        length=length,
        audience=audience,
        cta=cta,
        language=language,
        variants=int(variants),
        brand_rules=brand_rules or "",
        company=company,
    )

    try:
        if llm_is_online():
            raw = llm_generate(prompt, temperature=0.65, max_tokens=1200)
            # split on lines that contain only --
            chunks = [seg.strip() for seg in raw.split("\n--\n") if seg.strip()]
            if not chunks:
                chunks = [raw.strip()]
            while len(chunks) < int(variants):
                chunks.append(chunks[-1])
            outputs = chunks[: int(variants)]
        else:
            outputs = offline_fallback(
                content_type=content_type,
                topic=topic,
                bullets=bullets,
                tone=tone,
                length=length,
                audience=audience,
                cta=cta,
                language=language,
                variants=int(variants),
                company=company,
            )

        # Save to History (compatible with shared.history.add)
        meta = {
            "company": company,  # keep as dict to avoid asdict() errors
            "brief": {
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
                "brand_rules_used": bool(brand_rules),
            },
            "tags": ["content", content_type, platform, language],
        }
        add_history(
            kind="content",
            payload=meta,
            output=outputs if len(outputs) > 1 else outputs[0],
        )

        st.success("Draft(s) created!")

        # Show outputs + downloads
        for idx, draft in enumerate(outputs, start=1):
            st.markdown(f"#### Variant {idx}")
            st.markdown(draft)
            fname = f"variant_{idx}_{content_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                label=f"Download Variant {idx} (.txt)",
                data=draft.encode("utf-8"),
                file_name=fname,
                mime="text/plain",
                key=f"btn_dl_{idx}",
            )
            st.divider()

    except Exception as e:
        st.error(f"Error while generating: {e}")
