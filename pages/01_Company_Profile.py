# pages/01_Company_Profile.py
from __future__ import annotations
import streamlit as st

# --- soft imports -------------------------------------------------------------
try:
    from shared import state  # type: ignore
except Exception:  # minimal fallback so page still works
    class _Company(dict):
        pass

    class _State:
        def init(self): 
            st.session_state.setdefault("company", _Company(name="", industry="", size="Mid-market", goals=""))
            st.session_state.setdefault("brand_rules", "")
        def get_company(self):
            self.init()
            return st.session_state["company"]
        def set_company(self, comp):
            st.session_state["company"] = comp
        def get_brand_rules(self):
            self.init()
            return st.session_state.get("brand_rules", "")
        def set_brand_rules(self, txt: str):
            st.session_state["brand_rules"] = txt

    state = _State()  # type: ignore

# --- page ---------------------------------------------------------------------
st.set_page_config(page_title="Company Profile", page_icon="🏢", layout="wide")
state.init()
st.title("Company Profile")

co = state.get_company()
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    name = st.text_input("Company Name", value=co.get("name", ""))
with col2:
    industry = st.text_input("Industry / Sector", value=co.get("industry", ""))
with col3:
    size = st.selectbox(
        "Company Size",
        ["Small", "Mid-market", "Enterprise"],
        index=["Small","Mid-market","Enterprise"].index(co.get("size","Mid-market")),
    )

goals = st.text_area("Business Goals (one or two sentences)", value=co.get("goals", ""), height=100)

st.subheader("Brand rules (optional)")
brand_rules = st.text_area(
    "Paste brand do’s/don’ts or banned words",
    value=getattr(state, "get_brand_rules", lambda: "")(),
    height=140,
)

if st.button("Save profile", type="primary"):
    new_co = dict(name=name, industry=industry, size=size, goals=goals)
    state.set_company(new_co)
    if hasattr(state, "set_brand_rules"):
        state.set_brand_rules(brand_rules)
    st.success("Saved company profile and brand rules.")
