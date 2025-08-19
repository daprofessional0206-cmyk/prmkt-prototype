import streamlit as st
from shared import state

st.set_page_config(page_title="Company Profile", page_icon="🏢")

st.title("🏢 Company Profile")
st.write("Define your brand, goals, and rules once — used across all tools.")

company = state.get_company()

with st.form("company_form"):
    name = st.text_input("Company Name", value=company.get("name", ""))
    industry = st.text_input("Industry", value=company.get("industry", ""))
    size = st.text_input("Company Size", value=company.get("size", ""))
    goals = st.text_area("Business Goals", value=company.get("goals", ""), height=100)
    brand_rules = st.text_area(
        "Brand rules (do’s/don’ts, banned words, style guidelines)",
        value=state.get_brand_rules(),
        height=120,
    )

    submitted = st.form_submit_button("💾 Save Profile")
    if submitted:
        state.set_company(name=name, industry=industry, size=size, goals=goals)
        state.set_brand_rules(brand_rules)
        st.success("✅ Profile updated.")
