# pages/01_Company_Profile.py
from __future__ import annotations

import streamlit as st
from typing import Any, Dict

# --- shared state (works with the state module we've been using) ---
from shared import state

st.set_page_config(page_title="Company Profile", page_icon="🏢", layout="wide")
st.title("🏢 Company Profile")
st.caption("Set your name, industry, size, goals, audience & brand voice. All tools use this profile.")

# --- safety: init state and fetch current company profile ---
state.init()  # safe no-op if already initialized
co_raw = state.get_company()  # may be dict / object / None

def getv(obj: Any, key: str, default: str = "") -> str:
    """Read value from dict/object safely."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return str(obj.get(key, default) or "")
    # object-like
    return str(getattr(obj, key, default) or "")

# current values (with defaults)
name        = getv(co_raw, "name")
industry    = getv(co_raw, "industry")
size        = getv(co_raw, "size")
goals       = getv(co_raw, "goals")
audience    = getv(co_raw, "audience")
brand_voice = getv(co_raw, "brand_voice")
brand_rules = getv(co_raw, "brand_rules")
website     = getv(co_raw, "website")

# --- UI ---
c1, c2, c3 = st.columns([1.2, 1, 1])
with c1:
    name = st.text_input("Company Name", value=name, placeholder="Acme Technologies")
with c2:
    industry = st.text_input("Industry", value=industry, placeholder="Robotics / SaaS")
with c3:
    size = st.text_input("Company Size", value=size, placeholder="50–200")

goals = st.text_area(
    "Business goals (OKRs / outcomes)",
    value=goals,
    height=100,
    placeholder="E.g., Grow pipeline by 30%, launch RoboHub 2.0, expand to EU market.",
)

audience = st.text_input(
    "Primary audience (buyers / ICP / users)",
    value=audience,
    placeholder="Ops leaders at mid-market manufacturers; CTOs; plant managers",
)

brand_voice = st.text_input(
    "Brand voice / tone (short)",
    value=brand_voice,
    placeholder="Clear, confident, pragmatic; no hype.",
)

brand_rules = st.text_area(
    "Brand rules (do’s/don’ts, banned words; optional)",
    value=brand_rules,
    height=120,
    placeholder="Do: quantify outcomes; use plain English. Don’t: overpromise; avoid buzzwords like 'revolutionary'.",
)

website = st.text_input("Website (optional)", value=website, placeholder="https://acme.com")

# --- Save / Reset ---
col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("💾 Save Profile", use_container_width=True):
        new_profile: Dict[str, str] = {
            "name": name.strip(),
            "industry": industry.strip(),
            "size": size.strip(),
            "goals": goals.strip(),
            "audience": audience.strip(),
            "brand_voice": brand_voice.strip(),
            "brand_rules": brand_rules.strip(),
            "website": website.strip(),
        }
        state.set_company(new_profile)  # single place to persist
        st.success("Company profile saved. All tools will use this.")
        st.rerun()

with col_b:
    if st.button("🗑️ Clear Profile", use_container_width=True):
        state.set_company({})  # clear to empty profile
        st.success("Company profile cleared.")
        st.rerun()

# --- Preview ---
st.subheader("Preview")
st.markdown(
    f"""
**Name:** {name or "—"}  
**Industry:** {industry or "—"} · **Size:** {size or "—"}  
**Audience:** {audience or "—"}  
**Brand voice:** {brand_voice or "—"}  

**Goals:**  
{goals or "—"}

**Brand rules:**  
{brand_rules or "—"}

**Website:** {website or "—"}
"""
)
