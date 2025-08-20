# shared/state.py
from __future__ import annotations
import os
import time
from typing import Any, Dict, Tuple
import streamlit as st

# ---------- session init ----------
def init() -> None:
    """One-time session defaults."""
    if "company" not in st.session_state:
        st.session_state["company"] = {
            "name": "",
            "industry": "",
            "size": "Mid-market",
            "goals": "",
            "brand_rules": "",
        }
    if "history" not in st.session_state:
        st.session_state["history"] = []  # list[dict]
    if "cooldown_until" not in st.session_state:
        st.session_state["cooldown_until"] = 0.0


# ---------- company + brand rules ----------
def get_company() -> Dict[str, Any]:
    init()
    return dict(st.session_state["company"])

def set_company(updates: Dict[str, Any]) -> None:
    init()
    st.session_state["company"].update(updates)

def get_brand_rules() -> str:
    init()
    return st.session_state["company"].get("brand_rules", "") or ""

def set_brand_rules(text: str) -> None:
    init()
    st.session_state["company"]["brand_rules"] = text or ""


# ---------- OpenAI presence check (used by app + pages) ----------
def has_openai() -> bool:
    """True if an OpenAI key is available in secrets or env."""
    try:
        if st.secrets.get("openai_api_key"):
            return True
    except Exception:
        pass
    return bool(os.getenv("OPENAI_API_KEY"))


# ---------- simple cooldown guard ----------
def can_generate(seconds: int = 4) -> Tuple[bool, int]:
    """
    Returns (ok, remaining_seconds). If ok is False, tell the user to wait.
    """
    init()
    now = time.time()
    until = float(st.session_state.get("cooldown_until", 0.0))
    if now < until:
        return False, int(round(until - now))
    st.session_state["cooldown_until"] = now + max(0, seconds)
    return True, 0


# ---------- history helpers (light) ----------
def add_history(kind: str, payload: Dict[str, Any], output: Any, tags: list[str] | None = None) -> None:
    init()
    item = {
        "kind": kind,
        "payload": payload,
        "output": output,
        "tags": tags or [],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    st.session_state["history"].insert(0, item)

def get_history() -> list[Dict[str, Any]]:
    init()
    return list(st.session_state["history"])
