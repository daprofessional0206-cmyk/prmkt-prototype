# shared/state.py
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

import streamlit as st


# ---------- Internal helpers ----------
def _ensure_session_defaults() -> None:
    """Create all session keys this app expects, with safe defaults."""
    if "company" not in st.session_state:
        # Use a plain dict so existing code that does .get(...) works.
        st.session_state["company"] = {
            "name": "",
            "industry": "",
            "size": "Mid-market",
            "goals": "",
            "brand_rules": "",   # keep here so all pages can read/write
        }

    if "language" not in st.session_state:
        st.session_state["language"] = "English"

    if "history" not in st.session_state:
        st.session_state["history"] = []


# ---------- Public API ----------
def init() -> None:
    """Call at the top of each page."""
    _ensure_session_defaults()


def has_openai() -> bool:
    """
    True if an OpenAI key is available. We support:
      - st.secrets['openai_api_key']  (preferred on Streamlit Cloud)
      - environment variable OPENAI_API_KEY (fallback locally)
    """
    key = None
    try:
        key = st.secrets.get("openai_api_key", None)
    except Exception:
        # st.secrets may not exist locally
        key = None

    if not key:
        key = os.environ.get("OPENAI_API_KEY")

    # empty strings are also considered missing
    return bool(key and str(key).strip())


# --- Company profile (stored as a dict to avoid attribute errors) ---

def get_company() -> Dict[str, Any]:
    """Return the current company dict (never None)."""
    _ensure_session_defaults()
    return st.session_state["company"]


def set_company(company: Dict[str, Any]) -> None:
    """Replace the company dict safely."""
    _ensure_session_defaults()
    # only keep known keys; ignore random stuff to stay stable
    safe = {
        "name": company.get("name", ""),
        "industry": company.get("industry", ""),
        "size": company.get("size", "Mid-market"),
        "goals": company.get("goals", ""),
        "brand_rules": company.get("brand_rules", ""),
    }
    st.session_state["company"] = safe


def get_brand_rules() -> str:
    """Convenience accessor used by pages."""
    return get_company().get("brand_rules", "") or ""


def set_brand_rules(text: str) -> None:
    co = get_company()
    co["brand_rules"] = text or ""
    st.session_state["company"] = co


# --- Language (UI/LLM preference) ---

def get_language(default: str = "English") -> str:
    _ensure_session_defaults()
    return st.session_state.get("language", default)


def set_language(lang: str) -> None:
    _ensure_session_defaults()
    st.session_state["language"] = lang


# --- Small utilities used by pages (optional but harmless) ---

def ensure_key(name: str, default: Any) -> None:
    """Generic helper to create a key with a default."""
    if name not in st.session_state:
        st.session_state[name] = default
