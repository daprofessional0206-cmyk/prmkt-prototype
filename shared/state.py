# shared/state.py — session state bootstrap & accessors
from __future__ import annotations
import streamlit as st
from .types import Company, ContentBrief

def init():
    if "company" not in st.session_state:
        st.session_state.company = Company(
            name="Acme Innovations",
            industry="Technology",
            size="Mid-market",
            goals="Increase qualified demand, accelerate sales cycles, reinforce brand trust."
        )
    if "brand_rules" not in st.session_state:
        st.session_state.brand_rules = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.setdefault("history_filter_kind", ["Variants"])
    st.session_state.setdefault("history_filter_tags", [])
    st.session_state.setdefault("history_search", "")
    st.session_state.setdefault("content_brief", ContentBrief.defaults())

# company
def get_company() -> Company:
    return st.session_state.company

def set_company(c: Company) -> None:
    st.session_state.company = c

# brand rules
def get_brand_rules() -> str:
    return st.session_state.brand_rules

def set_brand_rules(text: str) -> None:
    st.session_state.brand_rules = text

# content brief
def get_brief() -> ContentBrief:
    return st.session_state.content_brief

def set_brief(b: ContentBrief) -> None:
    st.session_state.content_brief = b

# history (simple pass-through — richer utils in shared/history.py)
def get_history() -> list[dict]:
    return st.session_state.history
