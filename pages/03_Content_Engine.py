# pages/03_Content_Engine.py
from __future__ import annotations

import streamlit as st
from typing import List

from shared.state import get_company, add_history
try:
    from shared.llm import OPENAI_OK, llm_copy, make_prompt, offline_generic_copy, offline_press_release
except Exception:
    # Fallbacks for environments where shared.lmp is not available (prevents import errors)
    OPENAI_OK = False

    def make_prompt(brief, co):
        bullets = "\n".join(brief.bullets) if getattr(brief, "bullets", None) else ""
        return f"{brief.content_type}\nTopic: {brief.topic}\n{bullets}\nCTA: {brief.cta}"

    def llm_copy(prompt, temperature=0.65, max_tokens=1200):
        # Minimal deterministic placeholder for LLM output
        return f"Placeholder generated content for prompt:\n\n{prompt}"

    def offline_generic_copy(brief, co):
        bullets = "\n".join(f"- {b}" for b in (brief.bullets or []))
        return f"{brief.content_type}\n\nTopic: {brief.topic}\n\n{bullets}\n\nCTA: {brief.cta}"

    def offline_press_release(brief, co):
        # Simple press release fallback
        bullets = "\n".join(f"- {b}" for b in (brief.bullets or []))
        return (
            f"Press Release: {brief.topic}\n\n"
            f"{brief.content_type}\n\n"
            f"{bullets}\n\n"
            f"Call to Action: {brief.cta}"
        )

from shared.types import ContentBrief

st.set_page_config(page_title="Content Engine — A/B/C", page_icon="🧩", layout="wide")

st.header("Content Engine — A/B/C")

# --- Company context (readonly) ---
co = get_company()
with st.expander("Company context (from Profile)", expanded=False):
    st.write(co.__dict__)

# --- Brief form ---
left, right = st.columns([1, 1])

with left:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad", "Social Post", "Landing Page", "Email"],
        key="ce_type_pg",
    )
    platform = st.selectbox(
        "Platform (for Social/Ad)",
        ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"],
        key="ce_platform_pg",
    )
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0", key="ce_topic_pg")
    bullets_raw = st.text_area(
        "Key Points (bullets, one per line)",
        value="2× faster setup\nSOC 2 Type II\nSave 30% cost",
        height=120,
        key="ce_bullets_pg",
    )

with right:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"], key="ce_tone_pg")
    length = st.selectbox("Length", ["Short", "Medium", "Long"], key="ce_length_pg")
    audience = st.text_input("Audience (who is this for?)", value="Decision-makers", key="ce_audience_pg")
    cta = st.text_input("Call to Action", value="Book a demo", key="ce_cta_pg")

st.subheader("Brand rules (optional)")
brand_rules = st.text_area(
    "Paste brand do’s/don’ts or banned words (optional)",
    value="Avoid superlatives like 'best-ever'. Use 'customers' not 'clients'.",
    height=110,
    key="ce_brand_rules_pg",
)

col_lang, col_var = st.columns([2, 1])
with col_lang:
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0, key="ce_language_pg")
with col_var:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1, key="ce_variants_pg")

def bulletize(text: str) -> List[str]:
    return [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()][:15]

brief = ContentBrief(
    content_type=content_type,
    tone=tone,
    length=length,
    platform=platform,
    audience=audience or "Decision-makers",
    cta=cta,
    topic=topic,
    bullets=bulletize(bullets_raw),
    language=language,
    variants=int(variants),
    brand_rules=brand_rules or "",
)

issues = []
if not brief.topic.strip():
    issues.append("Add a topic/product name.")
if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

# --- Generate button ---
if st.button("Generate Variants (A/B/C)", key="btn_generate_variants_pg", use_container_width=True):
    if not brief.topic.strip():
        st.warning("Please enter a topic / offer first.")
        st.stop()

    try:
        outputs: List[str] = []
        if OPENAI_OK:
            raw = llm_copy(make_prompt(brief, co), temperature=0.65, max_tokens=1200)
            chunks = [seg.strip() for seg in raw.split("\n\n--\n\n") if seg.strip()]
            while len(chunks) < brief.variants:
                chunks.append(chunks[-1])
            outputs = chunks[:brief.variants]
        else:
            # Simple offline templates
            if brief.content_type == "Press Release":
                outputs = [offline_press_release(brief, co)]
            else:
                outputs = [offline_generic_copy(brief, co)]
            while len(outputs) < brief.variants:
                outputs.append(outputs[-1])

        # Save to history with tags
        add_history(
            kind="Variants",
            payload={"brief": brief.__dict__, "company": co.__dict__},
            output=outputs,
            tags=[brief.content_type, brief.language],
        )

        st.success("Draft(s) created!")
        for idx, draft in enumerate(outputs, start=1):
            st.markdown(f"### Variant {idx}")
            st.markdown(draft)
            st.download_button(
                label=f"Download Variant {idx} (.txt)",
                data=draft.encode("utf-8"),
                file_name=f"variant_{idx}_{brief.content_type.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                key=f"btn_dl_pg_{idx}",
                use_container_width=True,
            )
            st.divider()

    except Exception as e:
        st.error(f"Error while generating: {e}")

