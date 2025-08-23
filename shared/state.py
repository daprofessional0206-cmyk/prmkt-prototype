# shared/state.py  — resilient state layer (restore build)

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict
import streamlit as st


# ---------- Canonical company shape ----------
@dataclass
class Company:
    name: str = "Acme Innovations"
    industry: str = "Technology"
    size: str = "Mid-market"
    goals: str = "Increase qualified demand, accelerate sales cycles, reinforce brand trust…"
    brand_rules: str = ""   # keep brand guidelines here
    # (add more defaults later without breaking older pages)


# ---------- Bootstrapping ----------
def _ensure_bootstrap() -> None:
    """Make sure session has company + history with a stable shape."""
    # company
    if "company" not in st.session_state:
        st.session_state["company"] = asdict(Company())
    else:
        # normalize to dict and ensure all keys exist
        c = st.session_state["company"]
        if isinstance(c, Company):
            c = asdict(c)
        if not isinstance(c, dict):
            c = {}
        base = asdict(Company())
        base.update(c)  # user values override defaults
        st.session_state["company"] = base

    # history list exists so pages don’t crash
    if "history" not in st.session_state or not isinstance(st.session_state["history"], list):
        st.session_state["history"] = []


# ---------- Public helpers used by pages ----------
def get_company() -> Company:
    """Return Company dataclass (some older pages expect this)."""
    _ensure_bootstrap()
    cdict: Dict[str, Any] = st.session_state["company"]
    # fill missing with defaults
    base = Company()
    for k, v in base.__dict__.items():
        cdict.setdefault(k, v)
    return Company(**cdict)


def get_company_dict() -> Dict[str, Any]:
    """Return plain dict (newer pages prefer this)."""
    return asdict(get_company())


def set_company(**kwargs) -> None:
    """Update any fields on the company safely."""
    _ensure_bootstrap()
    cdict = get_company_dict()
    cdict.update({k: (v if v is not None else "") for k, v in kwargs.items()})
    st.session_state["company"] = cdict


def get_brand_rules() -> str:
    return get_company().brand_rules or ""


def set_brand_rules(text: str) -> None:
    set_company(brand_rules=text or "")


def has_openai() -> bool:
    """True if an API key is present in secrets."""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        key = ""
    return bool(key)
