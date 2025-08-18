# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st

# Shared modules in your repo
from shared import state
from shared.history import add as add_history

# LLM: works online (OpenAI) or offline fallback
try:
    from shared.llm import llm_copy, OPENAI_OK  # your helper (Phase 2)
except Exception:
    OPENAI_OK = False

    def llm_copy(prompt: str, temperature: float = 0.6, max_tokens: int = 900) -> str:
        # very simple offline stub
        return (
            "Draft:\n"
            "• Opening line tailored to the audience.\n"
            "• Benefit/feature #1\n"
            "• Benefit/feature #2\n"
            "• Clear CTA.\n"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Safe helpers for Company object (avoid dict .get errors)
# ─────────────────────────────────────────────────────────────────────────────
def safe_company_fields(company):
    """Return (name, industry, size) with safe defaults even if attributes are missing."""
    name = getattr(company, "name", "(Company)")
    industry = getattr(company, "industry", "Industry")
    size = getattr(company, "size", "Mid-market")
    return name, industry, size


def company_log_dict(company):
    """Stable dict for history/logging."""
    n, i, s = safe_company_fields(company)
    return {"name": n, "industry": i, "size": s}


# ─────────────────────────────────────────────────────────────────────────────
# Prompt builder (never uses company.get)
# ─────────────────────────────────────────────────────────────────────────────
def make_prompt(
    *,
    content_type: str,
    tone: str,
    length: str,
    platform: str,
    audience: str,
    cta: str,
    topic: str,
    bullets: list[str],
    language: str,
    brand_rules: str,
    variants: int,
    company,
) -> str:
    co_name, co_industry, co_size = safe_company_fields(company)

    bullets_md = "\n".join([f"- {b}" for b in bullets]) if bullets else "(no bullets provided)"
    rules = (brand_rules or "").strip() or "(none provided)"

    return f"""
You are an expert PR & Marketing copywriter.
Write clear, compelling, brand-safe copy. Keep facts generic unless provided.
Match the requested tone, audience, and length. If brand rules are provided, follow them and avoid banned words.
Return only the copy (no preface).

Generate {variants} distinct variant(s) of a {length.lower()} {content_type.lower()}.

Language: {language}.
Audience: {audience}. Tone: {tone}.
Company: {co_name} ({co_industry}, size: {co_size}).
Platform: {platform}.
Topic / Offer: {topic}

Key points:
{bullets_md}

Call to action: {cta}

Brand rules (follow & avoid banned words):
{rules}

Constraints:
- Brand-safe, factual only from provided info.
- Strong opening, clear structure, crisp CTA.
- If multiple variants are requested, make them clearly different.
- Separate each variant with a line containing exactly: ---VARIANT---
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────
st.title("Content Engine — A/B/C")

# Read current company + brand rules from shared.state
company = state.get_company()  # object with attributes
brand_rules = state.get_brand_rules()  # plain string (read-only here)

with st.expander("🧩 Brand Rules (read‑only)"):
    st.caption("Edit brand rules on the **Company Profile** page. They are applied automatically here.")
    st.code(brand_rules or "(none set)")

# Left/right column inputs
left, right = st.columns(2)

with left:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad", "Social Post", "Landing Page", "Email"],
        index=0,
    )
    platform = st.selectbox(
        "Platform (for Social/Ad)",
        ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"],
        index=0,
    )
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0")
    bullets_raw = st.text_area(
        "Key Points (bullets, one per line)",
        value="2× faster setup\nSOC 2 Type II\nSave 30% cost",
        height=120,
    )

with right:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"], index=0)
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=0)
    audience = st.text_input("Audience (who is this for?)", value="Decision-makers")
    cta = st.text_input("Call to Action", value="Book a demo")

# Language + variants
c1, c2 = st.columns([2, 1])
with c1:
    language = st.selectbox(
        "Language",
        ["English", "Spanish", "French", "German", "Hindi", "Japanese"],
        index=0,
    )
with c2:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1)

# Build bullets list
bullets = [ln.strip("•- \t") for ln in bullets_raw.splitlines() if ln.strip()]
bullets = bullets[:15]

# Generate button
if st.button("Generate A/B/C Variants", use_container_width=True, key="btn_ce_generate"):
    if not topic.strip():
        st.warning("Please enter a topic / offer first.")
    else:
        try:
            prompt = make_prompt(
                content_type=content_type,
                tone=tone,
                length=length,
                platform=platform,
                audience=audience,
                cta=cta,
                topic=topic,
                bullets=bullets,
                language=language,
                brand_rules=brand_rules or "",
                variants=int(variants),
                company=company,
            )

            # Call the LLM once; ask it to separate variants with ---VARIANT---
            raw = llm_copy(prompt, temperature=0.65, max_tokens=1200)
            chunks = [seg.strip() for seg in raw.split("---VARIANT---") if seg.strip()]

            # If LLM didn't separate clearly, just duplicate the first block
            while len(chunks) < int(variants):
                chunks.append(chunks[-1])

            outputs = chunks[: int(variants)]

            st.success("Draft(s) created!")
            # Display + download
            for idx, draft in enumerate(outputs, start=1):
                st.markdown(f"### Variant {idx}")
                st.markdown(draft)
                fname = f"variant_{idx}_{content_type.replace(' ', '_').lower()}.txt"
                st.download_button(
                    label=f"Download Variant {idx} (.txt)",
                    data=draft.encode("utf-8"),
                    file_name=fname,
                    mime="text/plain",
                    key=f"btn_dl_ce_{idx}",
                )
                st.divider()

            # Save to history (safe dict + useful tags)
            add_history(
                kind="Variants",
                payload={
                    "company": company_log_dict(company),
                    "content_type": content_type,
                    "tone": tone,
                    "length": length,
                    "platform": platform,
                    "audience": audience,
                    "cta": cta,
                    "topic": topic,
                    "bullets": bullets,
                    "language": language,
                    "brand_rules": brand_rules or "",
                    "variants": int(variants),
                },
                output=outputs,
                tags=[content_type, language, safe_company_fields(company)[1]],  # industry as tag
            )

        except Exception as e:
            st.error(f"Error while generating: {e!s}")
