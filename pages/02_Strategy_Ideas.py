import streamlit as st
from shared import state, history
from shared.llm import generate_copy

st.set_page_config(page_title="Strategy Ideas", page_icon="💡")

st.title("💡 Strategy Ideas")
st.write("Brainstorm bold PR & marketing angles quickly.")

state.throttle()

company = state.get_company()

topic = st.text_input("What’s the campaign about?", placeholder="Product launch, rebrand, crisis response...")
audience = st.text_input("Target audience", value="Decision-makers, media, customers")
tone = st.selectbox("Tone", ["Bold", "Professional", "Playful", "Inspirational"])
variants = st.slider("How many ideas?", 1, 5, 3)

if st.button("✨ Generate Ideas"):
    brief = {
        "content_type": "Strategy",
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "variants": variants,
        "brand_rules": state.get_brand_rules(),
    }
    outputs = generate_copy(company, brief)
    for o in outputs:
        st.markdown(o)
        st.divider()
    history.add("Strategy", brief, outputs, tags=["strategy"])
