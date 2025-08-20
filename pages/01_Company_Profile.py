# pages/01_Company_Profile.py
from __future__ import annotations
import streamlit as st
from shared import state

state.init()
st.set_page_config(page_title="Company Profile", layout="wide")

st.title("🏢 Company Profile")

co = state.get_company()

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    name = st.text_input("Company Name", value=co.get("name", ""))
with c2:
    industry = st.text_input("Industry / Sector", value=co.get("industry", ""))
with c3:
    size = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"], index=["Small","Mid-market","Enterprise"].index(co.get("size","Mid-market")))

goals = st.text_area("Business Goals (one or two sentences)", value=co.get("goals", ""), height=100)
brand_rules = st.text_area("Paste brand do’s/don’ts or banned words", value=state.get_brand_rules(), height=120)

if st.button("Save"):
    state.set_company({"name": name, "industry": industry, "size": size, "goals": goals})
    state.set_brand_rules(brand_rules)
    st.success("Saved.")
