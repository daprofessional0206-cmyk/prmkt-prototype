# shared/state.py
from __future__ import annotations

import streamlit as st
from dataclasses import dataclass, asdict

# ---- Company model ----
@dataclass
class Company:
    name: str = ""
    industry: str = ""
    size: str = "Mid-market"
    goals: str = ""


def init() -> None:
    """Ensure base state keys exist once per session."""
    st.session_state.setdefault("company", Company())
    st.session_state.setdefault("brand_rules", "")
    # you can add more defaults here if needed


def get_company() -> Company:
    # Return a dataclass (not a dict) so pages can use asdict() safely
    co = st.session_state.get("company_obj")
    if isinstance(co, Company):
        return co
    # fallback from any older dict to Company once
    d = st.session_state.get("company", {})
    if isinstance(d, dict):
        co = Company(
            name=d.get("name", ""),
            industry=d.get("industry", ""),
            size=d.get("size", "Mid-market"),
            goals=d.get("goals", ""),
        )
    else:
        co = Company()
    st.session_state["company_obj"] = co
    return co

def set_company(co: Company) -> None:
    st.session_state["company_obj"] = co


def get_company_dict() -> dict:
    """Convenience for saving to history, if needed."""
    return asdict(get_company())

# ---- Brand rules (plain text) ----
def get_brand_rules() -> str:
    # Always return a string (Streamlit widget defaults cannot be None)
    return st.session_state.get("brand_rules", "")

def set_brand_rules(text: str) -> None:
    st.session_state["brand_rules"] = text
