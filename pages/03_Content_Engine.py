# pages/03_Content_Engine.py
from __future__ import annotations
import streamlit as st

from shared import state, history
from shared.llm import llm_copy
from shared.exports import text_to_pdf_bytes, text_to_docx_bytes, join_variants

st.set_page_config(page_title="Content Engine", page_icon="📰", layout="wide")
st.title("📰 Content Engine")

state.init()
co = state.get_company()  # may be dict or a simple object

cols = st.columns(3)
with cols[0]:
    content_type = st.selectbox(
        "Content type",
        ["Press Release", "Ad Copy", "Landing Page", "Blog Post"],
    )
with cols[1]:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"])
with cols[2]:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

if st.button("Generate A/B/C Variants", use_container_width=True):
    company_name = co.get("name") if isinstance(co, dict) else getattr(co, "name", "")
    industry = co.get("industry") if isinstance(co, dict) else getattr(co, "industry", "")
    audience = co.get("audience") if isinstance(co, dict) else getattr(co, "audience", "")
    topic = co.get("topic") if isinstance(co, dict) else getattr(co, "topic", "New Launch")

    prompt = f"""
You are a senior PR/marketing copywriter.
Create three distinct {content_type} variants for:
- Company: {company_name} ({industry})
- Audience: {audience}
- Topic/Offer: {topic}
Tone: {tone}. Length: {length}.
Return only the copy for each variant, separated with a clear title line.
    """.strip()

    with st.spinner("Generating variants..."):
        try:
            raw = llm_copy(prompt)
        except Exception:
            raw = ""

    # Very light parser for 3 variants (fallback if model returns one block)
    parts = [p.strip() for p in raw.split("\n\n") if p.strip()]
    if len(parts) < 3:
        variants = [raw.strip() or "Draft:\n• Opening line tailored to the audience.\n• Benefit/feature #1\n• Benefit/feature #2\n• Clear CTA"]
    else:
        # keep the top 3 chunks as variants
        variants = parts[:3]

    # Show and export
    for i, v in enumerate(variants, 1):
        st.subheader(f"Variant {i}")
        st.write(v)

    joined = join_variants(variants)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Download A/B/C (.txt)",
            data=joined.encode("utf-8"),
            file_name="content_engine_variants.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "Download A/B/C (.docx)",
            data=text_to_docx_bytes(joined, title="Content Engine — A/B/C"),
            file_name="content_engine_variants.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            "Download A/B/C (.pdf)",
            data=text_to_pdf_bytes(joined, title="Content Engine — A/B/C"),
            file_name="content_engine_variants.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # Log to history
    try:
        history.add(
            kind="content",
            title=f"{content_type} — {tone}/{length}",
            payload={"variants": variants, "joined": joined},
            meta={"company": company_name, "type": content_type, "tone": tone, "length": length},
            tags=["content", content_type.lower(), tone.lower(), length.lower()],
        )
    except Exception:
        pass
