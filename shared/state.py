# shared/state.py
from __future__ import annotations
import streamlit as st
from typing import Dict, Any

def init() -> None:
    """Idempotent init of session keys."""
    ss = st.session_state
    ss.setdefault("company", {
        "name": "Acme Innovations",
        "industry": "Technology",
        "size": "Mid-market",
        "goals": "Increase qualified demand, accelerate sales cycles, reinforce brand trust…",
        "audience": "Decision-makers",
        "brand_rules": "Avoid superlatives like 'best-ever'. Use 'customers' not 'clients'.",
        "language": "English",
    })
    ss.setdefault("history", [])
    ss.setdefault("last_gen_ts", 0.0)

def get_company() -> Dict[str, Any]:
    init()
    return st.session_state["company"]

def set_company(updates: Dict[str, Any]) -> None:
    init()
    st.session_state["company"].update(updates)

def get_brand_rules() -> str:
    return get_company().get("brand_rules", "")

def set_brand_rules(text: str) -> None:
    set_company({"brand_rules": text})

def has_openai() -> bool:
    """True when OPENAI_API_KEY is present in secrets."""
    try:
        val = st.secrets.get("OPENAI_API_KEY", "")
        return bool(val)
    except Exception:
        return False
