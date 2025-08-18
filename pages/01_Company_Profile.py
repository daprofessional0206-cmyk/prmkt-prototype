# pages/01_Company_Profile.py
from __future__ import annotations
import streamlit as st
from shared import state, ui
from shared.types import Company

state.init()
ui.title("Company Profile")

co = state.get_company()
col1, col2, col3 = st.columns([2, 1.5, 1])
with col1:
    name = st.text_input("Company Name", value=co.name)
with col2:
    industry = st.text_input("Industry / Sector", value=co.industry)
with col3:
    size = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"],
                        index=["Small","Mid-market","Enterprise"].index(co.size))

goals = st.text_area("Business Goals (one or two sentences)", value=co.goals, height=90, key="cp_goals")

ui.divider()
st.subheader("Brand rules (optional)")
brand_rules = st.text_area("Paste brand do’s/don’ts or banned words", value=state.get_brand_rules(), height=120, key="cp_brand_rules")

if st.button("Save Profile", use_container_width=True, key="btn_save_profile"):
    new_co = Company(name=name, industry=industry, size=size, goals=goals)
    state.set_company(new_co)
    state.set_brand_rules(brand_rules or "")
    st.success("Saved company profile & brand rules.")
