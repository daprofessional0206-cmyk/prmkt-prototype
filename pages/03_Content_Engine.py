# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

# Optional shared imports; fallbacks if missing
try:
    from shared.llm import llm_copy  # your OpenAI wrapper
except Exception:
    llm_copy = None  # we’ll fallback

try:
    from shared.history import add_history  # your history helper
except Exception:
    def add_history(kind: str, payload: dict, output: str | List[str], tags: List[str] | None = None):
        rec = {"ts": datetime.utcnow().isoformat(timespec="seconds"), "kind": kind, "input": payload, "output": output}
        if tags:
            rec["tags"] = tags
        st.session_state.setdefault("history", [])
        st.session_state["history"].insert(0, rec)
        st.session_state["history"] = st.session_state["history"][:50]

try:
    from shared.state import get_company, get_brand_rules
except Exception:
    def get_company():
        # minimal safe fallback
        return {
            "name": st.session_state.get("cp_name", "Acme Innovations"),
            "industry": st.session_state.get("cp_industry", "Technology"),
            "size": st.session_state.get("cp_size", "Mid-market"),
            "goals": st.session_state.get("cp_goals", ""),
        }
    def get_brand_rules() -> str:
        return st.session_state.get("brand_rules", "")

# Exports (real files)
from shared.exports import text_to_docx_bytes, text_to_pdf_bytes


st.set_page_config(page_title="Presence — Content Engine", page_icon="📰", layout="wide")

st.title("📰 Content Engine — A/B/C Variants")
st.caption("Generate compelling PR & marketing drafts and export as .docx / .pdf / .txt.")

st.divider()

# Data classes
@dataclass
class Brief:
    content_type: str
    platform: str
    topic: str
    bullets: List[str]
    tone: str
    length: str
    audience: str
    cta: str
    language: str
    variants: int
    brand_rules: str

def bulletize(text: str) -> List[str]:
    return [ln.strip("•- \t") for ln in (text or "").splitlines() if ln.strip()][:15]


# --- left/right controls
left, right = st.columns([1, 1])

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

# Phase-2/3 additions
st.subheader("Branding & Controls")
brand_rules_default = get_brand_rules() or "Avoid superlatives like 'best-ever'. Use 'customers' not 'clients'."
brand_rules = st.text_area(
    "Brand rules (do’s/don’ts, banned words)",
    value=brand_rules_default,
    height=110,
    key="ce_brand_rules",
)

col_lang, col_var = st.columns([2, 1])
with col_lang:
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0, key="ce_language")
with col_var:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1, key="ce_variants")

brief = Brief(
    content_type=content_type,
    platform=platform,
    topic=topic,
    bullets=bulletize(bullets_raw),
    tone=tone,
    length=length,
    audience=audience or "Decision-makers",
    cta=cta,
    language=language,
    variants=int(variants),
    brand_rules=brand_rules or "",
)

# company
co = get_company()
company_name = co["name"]
company_industry = co["industry"]
company_size = co["size"]

# prompt builder
def make_prompt() -> str:
    bullets = "\n".join([f"- {b}" for b in brief.bullets]) if brief.bullets else "(no bullets provided)"
    rules = brief.brand_rules.strip() or "(none provided)"
    return f"""
Generate {brief.variants} distinct variant(s) of a {brief.length.lower()} {brief.content_type.lower()}.

Language: {brief.language}.
Audience: {brief.audience}. Tone: {brief.tone}.
Company: {company_name} (Industry: {company_industry}, Size: {company_size}).
Topic / Offer: {brief.topic}

Key points:
{bullets}

Call to action: {brief.cta}

Brand rules (follow & avoid banned words):
{rules}

Output formatting:
Return variants separated by a line with exactly: ---

Constraints:
- Brand-safe, factual from provided info only.
- Strong opening, clear structure, crisp CTA.
- If multiple variants are requested, make them clearly different.
""".strip()


def offline_fallback() -> List[str]:
    # simple offline template — one or more variants
    opening = {
        "Ad": "Attention, innovators!",
        "Social Post": "Quick update:",
        "Landing Page": "Welcome—here’s how we help:",
        "Email": "Hi there,",
        "Press Release": "FOR IMMEDIATE RELEASE",
    }.get(brief.content_type, "Here’s something useful:")
    bullets_md = "\n".join([f"• {b}" for b in brief.bullets]) if brief.bullets else "• Add 2–3 benefits"
    draft = f"""{opening}

{company_name} presents **{brief.topic}** for {brief.audience}.
Tone: {brief.tone}. Length: {brief.length}. Language: {brief.language}.

What you’ll get:
{bullets_md}

Next step: **{brief.cta}**
"""
    return [draft for _ in range(brief.variants)]


st.divider()

# generate
if st.button("Generate A/B/C Variants", type="primary", use_container_width=True, key="btn_generate_variants"):
    if not brief.topic.strip():
        st.warning("Please enter a topic / offer first.")
        st.stop()

    with st.spinner("Generating..."):
        outputs: List[str] = []
        try:
            p = make_prompt()
            if llm_copy is not None and st.secrets.get("OPENAI_API_KEY"):
                raw = llm_copy(p, temperature=0.65, max_tokens=1200)
                # split by our delimiter
                chunks = [seg.strip() for seg in raw.split("---") if seg.strip()]
                if not chunks:
                    chunks = [raw.strip()]
                while len(chunks) < brief.variants:
                    chunks.append(chunks[-1])
                outputs = chunks[:brief.variants]
            else:
                outputs = offline_fallback()
        except Exception as e:
            st.error(f"LLM error: {e}")
            outputs = offline_fallback()

    # show + save + downloads
    for idx, draft in enumerate(outputs, start=1):
        st.markdown(f"#### Variant {idx}")
        st.markdown(draft)

        colA, colB, colC = st.columns(3)
        with colA:
            st.download_button(
                label=f"Download Variant {idx} (.txt)",
                data=draft.encode("utf-8"),
                file_name=f"variant_{idx}.txt",
                mime="text/plain",
                key=f"dl_txt_{idx}",
            )
        with colB:
            st.download_button(
                label=f"Download Variant {idx} (.docx)",
                data=text_to_docx_bytes(f"{brief.content_type} — Variant {idx}", draft),
                file_name=f"variant_{idx}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_docx_{idx}",
            )
        with colC:
            st.download_button(
                label=f"Download Variant {idx} (.pdf)",
                data=text_to_pdf_bytes(f"{brief.content_type} — Variant {idx}", draft),
                file_name=f"variant_{idx}.pdf",
                mime="application/pdf",
                key=f"dl_pdf_{idx}",
            )
        st.divider()

    # one consolidated history record
    add_history(
        "Variants",
        payload={
            "brief": asdict(brief),
            "company": co,
        },
        output=outputs,
        tags=["variants", brief.content_type, brief.tone, brief.language],
    )
    st.success("Draft(s) created and saved to history.")
