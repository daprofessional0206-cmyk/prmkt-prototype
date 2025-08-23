# shared/state.py — resilient, backward-compatible state layer

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict
import streamlit as st


# ── Company shape (add fields safely over time) ───────────────────────────────
@dataclass
class Company:
    name: str = "Acme Innovations"
    industry: str = "Technology"
    size: str = "Mid-market"
    goals: str = "Increase qualified demand, accelerate sales cycles, reinforce brand trust…"
    brand_rules: str = ""  # central place for brand guidelines

    # Allow dict-style access on the dataclass (so co["name"] works)
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    # Allow dict-style get (so co.get("goals", "") works)
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


# ── Internal bootstrap ────────────────────────────────────────────────────────
def _ensure_bootstrap() -> None:
    """Ensure session has a normalized company dict and a history list."""
    # Ensure company block
    base_dict = asdict(Company())
    c = st.session_state.get("company")

    if isinstance(c, Company):
        # normalize old dataclass to dict
        c = asdict(c)

    if not isinstance(c, dict):
        c = {}

    # merge defaults
    merged = {**base_dict, **c}
    st.session_state["company"] = merged

    # Ensure history list exists
    if not isinstance(st.session_state.get("history"), list):
        st.session_state["history"] = []


# ── Public API used by pages ─────────────────────────────────────────────────
def init() -> None:
    """Backwards-compat no-op that initializes session state."""
    _ensure_bootstrap()


def get_company() -> Company:
    """Return a Company object (supports attribute AND dict-style access)."""
    _ensure_bootstrap()
    cdict: Dict[str, Any] = st.session_state["company"]
    # fill missing keys with defaults
    base = Company()
    for k, v in base.__dict__.items():
        cdict.setdefault(k, v)
    # return as Company instance (with __getitem__/get helpers)
    return Company(**cdict)


def get_company_dict() -> Dict[str, Any]:
    """Return a plain dict. Some pages prefer this."""
    return asdict(get_company())


def set_company(**kwargs) -> None:
    """Update any fields on the company safely."""
    _ensure_bootstrap()
    cdict = get_company_dict()
    for k, v in kwargs.items():
        cdict[k] = "" if v is None else v
    st.session_state["company"] = cdict


def get_brand_rules() -> str:
    """Convenience accessor for brand rules."""
    return get_company().brand_rules or ""


def set_brand_rules(text: str) -> None:
    set_company(brand_rules=text or "")


def has_openai() -> bool:
    """True if an API key is present in secrets (works locally & on Cloud)."""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        key = ""
    return bool(key)
