from __future__ import annotations
import streamlit as st
from dataclasses import asdict
from shared import ui, state, history
from shared import llm

st.set_page_config(page_title="Content Engine", page_icon="📝", layout="wide")
ui.inject_css()
ui.page_title("Content Engine", "Generate press releases, ads, landing pages, blogs, and social posts.")

state.init()
co = state.get_company()

cols = st.columns(3)
with cols[0]:
    content_type = st.selectbox("Content Type", ["Press Release", "Ad Copy", "Landing Page", "Blog Post", "Social Post"], index=0)
with cols[1]:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
with cols[2]:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

cols2 = st.columns(2)
with cols2[0]:
    lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], index=0)
with cols2[1]:
    n = st.number_input("Variants (A/B/C…)", min_value=1, max_value=5, value=1, step=1)

if st.button("Generate A/B/C Variants", type="primary"):
    drafts, err = llm.variants(content_type, int(n), co, tone, length, lang)

    history.add_history(
        "variants",
        payload={
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "language": lang,
            "company": asdict(co),
        },
        result=drafts,
        tags=["variants", content_type, tone, length, lang] + ([co.size] if co.size else []),
    )

    if err:
        st.error("Could not generate right now (LLM issue). Showing a minimal fallback draft.")
        for i, d in enumerate(drafts, 1):
            st.markdown(f"**Variant {i}**")
            st.code(d)
        st.caption(f"Details: {err}")
    else:
        st.success("Draft(s) created!")
        for i, d in enumerate(drafts, 1):
            with st.expander(f"Variant {i}"):
                st.write(d)
                st.download_button(f"Download Variant {i} (.txt)", d, file_name=f"variant_{i}.txt")
