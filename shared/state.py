# shared/state.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any
import streamlit as st

@dataclass
class Company:
    name: str = "Acme Innovations"
    industry: str = "Technology"
    size: str = "Mid-market"
    goals: str = "Increase qualified demand, accelerate sales cycles, reinforce brand trust…"
    brand_rules: str = ""

# ---- bootstrap ----
def _ensure_bootstrap() -> None:
    if "company" not in st.session_state:
        st.session_state["company"] = asdict(Company())
    if "history" not in st.session_state:
        st.session_state["history"] = []

def get_company() -> Company:
    _ensure_bootstrap()
    c = st.session_state["company"]
    if isinstance(c, dict):
        return Company(**{**Company().__dict__, **c})
    if isinstance(c, Company):
        return c
    return Company()

def get_company_dict() -> Dict[str, Any]:
    return dict(get_company().__dict__)

def set_company(**kwargs) -> None:
    c = get_company().__dict__
    c.update(kwargs)
    st.session_state["company"] = c

def get_brand_rules() -> str:
    return get_company().brand_rules or ""

def set_brand_rules(text: str) -> None:
    set_company(brand_rules=text or "")

def has_openai() -> bool:
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        key = ""
    return bool(key)
