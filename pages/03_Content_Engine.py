import streamlit as st
from shared import state, history
from shared.llm import generate_copy

st.set_page_config(page_title="Content Engine", page_icon="📝")

st.title("📝 Content Engine")
st.write("Generate press releases, ads, landing pages, blogs, and social posts.")

state.throttle()

company = state.get_company()

content_type = st.selectbox("Content Type", ["Press Release", "Ad Copy", "Landing Page", "Blog Post", "Social Media Post"])
platform = st.text_input("Platform (optional)", placeholder="LinkedIn, Instagram, Website...")
topic = st.text_input("Topic / Product / Offer", placeholder="Acme RoboHub launch")
bullets = st.text_area("Key points (one per line)").splitlines()
tone = st.selectbox("Tone", ["Professional", "Casual", "Bold", "Inspirational"])
length = st.selectbox("Length", ["Short", "Medium", "Long"])
audience = st.text_input("Audience", value="Decision-makers")
cta = st.text_input("Call to Action", value="Get started today.")
language = st.text_input("Language", value="English")
variants = st.slider("How many variants?", 1, 5, 2)

if st.button("⚡ Generate Content"):
    brief = {
        "content_type": content_type,
        "platform": platform,
        "topic": topic,
        "bullets": bullets,
        "tone": tone,
        "length": length,
        "audience": audience,
        "cta": cta,
        "language": language,
        "variants": variants,
        "brand_rules": state.get_brand_rules(),
    }
    outputs = generate_copy(company, brief)
    for o in outputs:
        st.markdown(o)
        st.divider()
    history.add("Content", brief, outputs, tags=["content", content_type])
