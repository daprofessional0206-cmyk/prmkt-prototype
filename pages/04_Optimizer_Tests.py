import streamlit as st
from shared import state, history
from shared.llm import generate_copy

st.set_page_config(page_title="Optimizer Tests", page_icon="🧪")

st.title("🧪 Optimizer Tests")
st.write("Test different tones, lengths, or styles to optimize messaging.")

state.throttle()

company = state.get_company()

base = st.text_area("Paste base copy to optimize", height=150)
dimension = st.selectbox("Test dimension", ["Tone", "Length", "CTA", "Style"])
variants = st.slider("How many variations?", 2, 6, 3)

if st.button("🔍 Run Test"):
    brief = {
        "content_type": "Optimizer",
        "topic": base,
        "tone": "Varied" if dimension == "Tone" else "Professional",
        "length": "Varied" if dimension == "Length" else "Medium",
        "audience": "Decision-makers",
        "cta": "Varied" if dimension == "CTA" else "Learn more.",
        "variants": variants,
        "brand_rules": state.get_brand_rules(),
    }
    outputs = generate_copy(company, brief)
    for i, o in enumerate(outputs, start=1):
        st.markdown(f"**Variant {i}:**\n\n{o}")
        st.divider()
    history.add("Optimizer", brief, outputs, tags=["optimizer", dimension])
