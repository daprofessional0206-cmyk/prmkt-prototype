# shared/state.py
from __future__ import annotations

import streamlit as st
from dataclasses import dataclass, asdict


@dataclass
class Company:
    name: str = "Acme Innovations"
    industry: str = "Technology"
    size: str = "Mid-market"
    goals: str = ""


def init() -> None:
    """Ensure base state keys exist once per session."""
    st.session_state.setdefault("company", Company())
    st.session_state.setdefault("brand_rules", "")
    # you can add more defaults here if needed


def get_company() -> Company:
    init()
    return st.session_state["company"]


def set_company(co: Company) -> None:
    st.session_state["company"] = co


def get_company_dict() -> dict:
    """Convenience for saving to history, if needed."""
    return asdict(get_company())
