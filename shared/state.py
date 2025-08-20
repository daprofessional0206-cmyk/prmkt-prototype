from __future__ import annotations
import os
import streamlit as st
from .types import Company


def init() -> None:
    st.session_state.setdefault("company", Company())
    st.session_state.setdefault("history", [])


def get_company() -> Company:
    init()
    co = st.session_state["company"]
    if isinstance(co, dict):
        co = Company(**co)
        st.session_state["company"] = co
    return co


def set_company(**kwargs) -> Company:
    co = get_company()
    for k, v in kwargs.items():
        if hasattr(co, k):
            setattr(co, k, v)
    return co


def get_brand_rules() -> str:
    return get_company().brand_rules or ""


def has_openai() -> bool:
    return bool(st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY"))
