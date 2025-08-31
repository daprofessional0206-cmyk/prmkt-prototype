# pages/03_Content_Engine.py
from __future__ import annotations
import streamlit as st
from shared import ui, state, history
from shared.llm import llm_copy
from shared.exports import text_to_docx_bytes, text_to_pdf_bytes

state.init()
ui.page_title("Content Engine (A/B/C)", "Generate press releases, ads, posts, emails, landing pages.")

co = state.get_company()

left, right = st.columns(2)
with left:
    content_type = st.selectbox("Content Type", ["Press Release","Ad","Social Post","Landing Page","Email"])
    platform = st.selectbox("Platform (if relevant)", ["Generic","LinkedIn","Instagram","X/Twitter","YouTube","Search Ad"])
    topic = st.text_input("Topic / Offer", value="Launch of Acme RoboHub 2.0")
    bullets = st.text_area("Key points (one per line)", value="2× faster setup\nSOC 2 Type II\nSave 30% cost", height=110)
with right:
    tone = st.selectbox("Tone", ["Professional","Friendly","Bold","Neutral"], index=0)
    length = st.selectbox("Length", ["Short","Medium","Long"], index=1)
    audience = st.text_input("Audience", value="Decision-makers")
    cta = st.text_input("Call to Action", value="Book a demo")

brand_rules = state.get_brand_rules()
col3, col4 = st.columns([2,1])
with col3:
    lang = st.selectbox("Language", ["English","Spanish","French","German","Hindi","Japanese"], index=0)
with col4:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=2, step=1)

if st.button("Generate Variants", type="primary"):
    bullet_lines = "\n".join([f"- {b.strip()}" for b in bullets.splitlines() if b.strip()]) or "- (add key benefits)"
    prompt = (
        f"Generate {variants} distinct {length.lower()} {content_type.lower()} variants in {lang}.\n"
        f"Company: {co.name} (Industry: {co.industry}, Size: {co.size}).\n"
        f"Audience: {audience}. Tone: {tone}. Platform: {platform}.\n"
        f"Topic: {topic}\n\nKey points:\n{bullet_lines}\n\n"
        f"CTA: {cta}\n\nBrand rules (follow; avoid banned words):\n{brand_rules or '(none)'}\n\n"
        f"Return only the copy. Separate variants clearly with '\n---\n'."
    )
    raw = llm_copy(prompt, temperature=0.65, max_tokens=1100)
    parts = [p.strip() for p in raw.split("\n---\n") if p.strip()]
    if not parts:
        parts = [raw.strip()]

    joined = ("\n\n" + ("—"*40) + "\n\n").join(parts)
    st.success("Draft(s) created")
    for i, p in enumerate(parts, start=1):
        st.markdown(f"#### Variant {i}")
        st.markdown(p)

    history.add(
        kind="variants",
        text=joined,
        payload={
            "content_type": content_type, "platform": platform, "topic": topic,
            "tone": tone, "length": length, "audience": audience, "cta": cta,
            "language": lang, "variants": int(variants), "company": state.get_company_as_dict()},
        tags=["variants", content_type, tone, length, lang],
        meta={"company": co.name}
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download A/B/C (.docx)", data=text_to_docx_bytes(joined),
                           file_name="variants.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c2:
        st.download_button("Download A/B/C (.pdf)", data=text_to_pdf_bytes(joined),
                           file_name="variants.pdf", mime="application/pdf")
