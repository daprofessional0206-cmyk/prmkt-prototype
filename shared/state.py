# shared/state.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime
import time
import streamlit as st


# -----------------------------
# Company & Brand state helpers
# -----------------------------

@dataclass
class Company:
    name: str = "Acme Innovations"
    industry: str = "Technology"
    size: str = "Mid-market"
    goals: str = "Increase qualified demand, accelerate sales cycles, reinforce brand trust…"


def _init_company_if_needed() -> None:
    if "company" not in st.session_state or not isinstance(st.session_state["company"], dict):
        st.session_state["company"] = asdict(Company())


def get_company() -> Dict[str, str]:
    """Return company dict with keys: name, industry, size, goals."""
    _init_company_if_needed()
    return st.session_state["company"]


def set_company(**kwargs) -> None:
    """Update any of: name, industry, size, goals."""
    _init_company_if_needed()
    st.session_state["company"].update({k: v for k, v in kwargs.items() if v is not None})


def get_brand_rules() -> str:
    return st.session_state.get("brand_rules", "")


def set_brand_rules(text: str) -> None:
    st.session_state["brand_rules"] = text or ""


# -----------------------------
# Guardrails / Throttling
# -----------------------------

def throttle(seconds: int = 6) -> None:
    """Prevent accidental double-click runs."""
    now = time.time()
    last = st.session_state.get("last_gen_ts", 0.0)
    if now - last < seconds:
        wait = int(seconds - (now - last))
        st.info(f"⏳ Please wait {wait}s before generating again.")
        st.stop()
    st.session_state["last_gen_ts"] = now


def friendly_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
