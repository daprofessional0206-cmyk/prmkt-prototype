# pages/03_Content_Engine.py
from __future__ import annotations
import streamlit as st
from typing import List
from shared import state, history
from shared.exports import text_to_txt_bytes, text_to_docx_bytes, text_to_pdf_bytes

# LLM
try:
    from shared.llm import llm_copy
    HAS_LLM = True
except Exception:
    HAS_LLM = False

st.set_page_config(page_title="Presence • Content Engine", page_icon="📰", layout="wide")
state.init()
co = state.get_company()

st.title("📰 Content Engine (A/B/C)")
st.caption("Generate PR & marketing copy aligned to your brand rules & audience.")

left, right = st.columns([1, 1])
with left:
    content_type = st.selectbox("Content Type", ["Press Release", "Ad", "Social Post", "Landing Page", "Email"])
    platform = st.selectbox("Platform (for Social/Ad)", ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"])
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0")
    bullets_raw = st.text_area("Key Points (bullets, one per line)", value="2× faster setup\nSOC 2 Type II\nSave 30% cost", height=110)

with right:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"])
    length = st.selectbox("Length", ["Short", "Medium", "Long"])
    audience = st.text_input("Audience (who is this for?)", value=co.get("audience", "Decision-makers"))
    cta = st.text_input("Call to Action", value="Book a demo")

st.subheader("Brand rules (optional)")
brand_rules = st.text_area("Do’s / Don’ts / Banned words", value=co.get("brand_rules", ""), height=110)

col_lang, col_var = st.columns([2, 1])
with col_lang:
    lang = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0)
with col_var:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1)

bullets: List[str] = [ln.strip("•- \t") for ln in bullets_raw.splitlines() if ln.strip()]
bullets = bullets[:15]

def _make_prompt() -> str:
    b = "\n".join([f"- {x}" for x in bullets]) if bullets else "(no bullets)"
    rules = brand_rules.strip() or "(none provided)"
    return (
        f"Generate {variants} distinct variant(s) of a {length.lower()} {content_type.lower()}.\n\n"
        f"Language: {lang}.\n"
        f"Audience: {audience}. Tone: {tone}.\n"
        f"Company: {co.get('name')} (Industry: {co.get('industry')}, Size: {co.get('size')}).\n"
        f"Topic / Offer: {topic}\n\n"
        f"Key points:\n{b}\n\n"
        f"Call to action: {cta}\n\n"
        f"Brand rules (follow & avoid banned words):\n{rules}\n\n"
        f"Constraints:\n"
        f"- Brand-safe, factual from provided info only.\n"
        f"- Strong opening, clear structure, crisp CTA.\n"
        f"- If multiple variants are requested, make them clearly different.\n"
        f"Return each variant separated by a line with just: --"
    )

if st.button("Generate A/B/C Variants", type="primary"):
    try:
        prompt = _make_prompt()
        outputs: List[str] = []
        if HAS_LLM and state.has_openai():
            raw = llm_copy(prompt, temperature=0.65, max_tokens=1200)
            chunks = [seg.strip() for seg in raw.split("\n--\n") if seg.strip()]
            while len(chunks) < int(variants):
                chunks.append(chunks[-1])
            outputs = chunks[: int(variants)]
        else:
            # Offline very simple template
            base = (
                "Draft:\n"
                f"- Opening line tailored to {audience}.\n"
                f"- Benefit/feature #1\n"
                f"- Benefit/feature #2\n"
                f"- Clear CTA: {cta}\n"
            )
            outputs = [base] * int(variants)

        st.success("Draft(s) created!")
        for idx, d in enumerate(outputs, start=1):
            st.markdown(f"#### Variant {idx}")
            st.markdown(d)
            # downloads
            fname = f"variant_{idx}_{content_type.replace(' ','_').lower()}.txt"
            st.download_button(f"Download Variant {idx} (.txt)", data=text_to_txt_bytes(d), file_name=fname, mime="text/plain", key=f"dl_txt_{idx}")
            st.download_button(f"Download Variant {idx} (.docx)", data=text_to_docx_bytes(d), file_name=fname.replace(".txt", ".docx"), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_docx_{idx}")
            st.download_button(f"Download Variant {idx} (.pdf)", data=text_to_pdf_bytes(d), file_name=fname.replace(".txt", ".pdf"), mime="application/pdf", key=f"dl_pdf_{idx}")
            st.divider()

        # Unified history record
        history.add(
            kind="content",
            payload={
                "company": co,
                "content_type": content_type,
                "platform": platform,
                "topic": topic,
                "tone": tone,
                "length": length,
                "audience": audience,
                "cta": cta,
                "language": lang,
                "variants": int(variants),
                "bullets": bullets,
            },
            output=outputs if len(outputs) > 1 else (outputs[0] if outputs else ""),
            tags=["content", content_type, platform, tone, length, lang],
        )
    except Exception as e:
        st.error(f"Error while generating: {e}")
