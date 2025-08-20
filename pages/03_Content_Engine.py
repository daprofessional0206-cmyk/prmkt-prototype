# pages/03_Content_Engine.py
from __future__ import annotations
import streamlit as st
from shared import state
from shared.llm import is_openai_ready, llm_copy

state.init()
st.set_page_config(page_title="Content Engine", layout="wide")
st.title("📰 Content Engine")
st.caption("Generate press releases, ads, landing pages, blogs, and social posts.")

ok, remaining = state.can_generate(4)
if not ok:
    st.info(f"Please wait {remaining}s before generating again.")
    st.stop()

if not is_openai_ready():
    st.warning("OpenAI key not configured. Set it in environment/Streamlit secrets.")
    st.stop()

# Basic controls
colA, colB, colC = st.columns([2, 1, 1])
with colA:
    content_type = st.selectbox("Content Type", ["Press Release", "Ad", "Landing Page", "Blog Post", "Social Post"])
with colB:
    tone = st.selectbox("Tone", ["Neutral", "Bold", "Friendly", "Formal"])
with colC:
    length = st.selectbox("Length", ["Short", "Medium", "Long"])

topic = st.text_input("Topic / Product / Offer", placeholder="e.g., Launch of Acme RoboHub 2.0")
bullets = st.text_area("Key points (one per line)", placeholder="• point 1\n• point 2\n• point 3", height=120)

company = state.get_company()
rules = state.get_brand_rules()

prompt = f"""
Write a {content_type}.

Audience tone: {tone}. Length: {length}.
Company: {company.get('name','')} • Industry: {company.get('industry','')} • Size: {company.get('size','')}
Goals: {company.get('goals','')}

Topic/Offer: {topic}

Key points:
{bullets}

Brand rules (if any): {rules if rules else '—'}

Return polished, publishable copy (no placeholders). Avoid disallowed brand terms.
"""

if st.button("Generate A/B/C Variants"):
    try:
        # Simple single variant for now; you can loop for A/B/C if you want.
        out = llm_copy(prompt).strip()
        st.success("Draft(s) created!")
        st.subheader("Variant 1")
        st.markdown(out)
        state.add_history("variants", {
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "topic": topic,
            "bullets": bullets,
            "language": "English",
        }, out, tags=[content_type, "English"])
    except Exception as e:
        st.error(str(e))
