# shared/state.py
from __future__ import annotations
import streamlit as st
from dataclasses import dataclass, asdict

@dataclass
class CompanyProfile:
    name: str = "Acme Innovations"
    industry: str = "Technology"
    size: str = "Mid-market"
    goals: str = ""

def init() -> None:
    st.session_state.setdefault("company", CompanyProfile())
    st.session_state.setdefault("brand_rules", "")
    st.session_state.setdefault("history", [])
    # cache: None / client
    st.session_state.setdefault("_openai_ready", None)

def set_company(**kwargs) -> None:
    c = st.session_state.get("company", CompanyProfile())
    for k, v in kwargs.items():
        if hasattr(c, k):
            setattr(c, k, v)
    st.session_state["company"] = c

def get_company() -> CompanyProfile:
    c = st.session_state.get("company")
    if isinstance(c, dict):
        # migrate old dict to dataclass
        c = CompanyProfile(**c)
        st.session_state["company"] = c
    return c

def get_company_as_dict() -> dict:
    c = get_company()
    return asdict(c)

def get_brand_rules() -> str:
    return st.session_state.get("brand_rules", "")

def set_brand_rules(text: str) -> None:
    st.session_state["brand_rules"] = text

def has_openai() -> bool:
    if st.session_state.get("_openai_ready") is not None:
        return bool(st.session_state["_openai_ready"])
    ok = bool(st.secrets.get("OPENAI_API_KEY", ""))
    st.session_state["_openai_ready"] = ok
    return ok