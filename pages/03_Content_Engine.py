# pages/03_Content_Engine.py
from __future__ import annotations
import streamlit as st
from shared import state, llm, history
from shared.exports import text_to_docx_bytes, text_to_pdf_bytes

st.set_page_config(page_title="Content Engine", page_icon="📰", layout="wide")
st.title("📰 Content Engine")
st.caption("Create press releases, ads, posts, landing pages, blogs — with brand-safe copy.")

state.init()
co = state.get_company()

c1, c2, c3 = st.columns(3)
with c1:
    content_type = st.selectbox("Content Type", ["Press Release", "Ad Copy", "Landing Page", "Blog Post"], index=0)
with c2:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
with c3:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

topic = st.text_input("Topic / Offer (what is this about?)", value=co.get("topic",""))

if "ce_output" not in st.session_state:
    st.session_state["ce_output"] = ""

if st.button("Generate A/B/C Variants", use_container_width=True):
    prompt = f"""Write {content_type} variants (A/B/C) for:
Company: {co.get('name','')} (Industry: {co.get('industry','')}, Audience: {co.get('audience','')}).
Brand voice: {co.get('brand_voice','')}. Language: English.
Topic/Offer: {topic}

Key points:
- Benefits
- Proof
- Clear CTA

Tone: {tone}. Length: {length}.
Return three labeled variants."""
    try:
        out = llm.llm_copy(prompt)
        st.session_state["ce_output"] = out
        history.add(
            tool="Content Engine",
            payload={"content_type": content_type, "tone": tone, "length": length, "topic": topic, "company": co},
            output=out,
            tags=["variants", content_type, tone, length],
            meta={"company": co.get("name","N/A")},
        )
    except Exception as e:
        st.error(f"Error while generating: {e}")

out = st.session_state.get("ce_output", "")
if out:
    st.markdown("### Variants")
    st.markdown(out)

    # Stacked buttons to avoid layout error
    st.download_button("Download A/B/C (.txt)", out.encode("utf-8"), "variants.txt", "text/plain", use_container_width=True)
    st.download_button("Download A/B/C (.docx)", text_to_docx_bytes(out),
                       "variants.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       use_container_width=True)
    st.download_button("Download A/B/C (.pdf)", text_to_pdf_bytes(out),
                       "variants.pdf", "application/pdf", use_container_width=True)
