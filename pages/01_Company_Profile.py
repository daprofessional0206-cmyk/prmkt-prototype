from __future__ import annotations
import streamlit as st
from shared import ui, state

st.set_page_config(page_title="Company Profile", page_icon="🏢", layout="wide")
ui.inject_css()
ui.page_title("Company Profile")

state.init()
co = state.get_company()

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    name = st.text_input("Company Name", value=co.name)
with c2:
    industry = st.text_input("Industry / Sector", value=co.industry)
with c3:
    size = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"], index=["Small","Mid-market","Enterprise"].index(co.size or "Mid-market"))

goals = st.text_area("Business Goals (one or two sentences)", value=co.goals, height=90)
brand_rules = st.text_area("Brand rules (do’s/don’ts, banned words; optional)", value=co.brand_rules, height=120)

if st.button("Save profile", type="primary"):
    state.set_company(name=name, industry=industry, size=size, goals=goals, brand_rules=brand_rules)
    st.success("Saved. Other pages will now use your profile.")
