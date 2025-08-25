# shared/state.py
from __future__ import annotations
import os
from typing import Any, Dict
import streamlit as st

# ---- Keep old API working (some pages still call experimental_rerun)
if not hasattr(st, "experimental_rerun"):
    st.experimental_rerun = st.rerun  # type: ignore

class DotDict(dict):
    """Dict with attribute access; also offers .asdict() like a dataclass."""
    def __getattr__(self, key: str) -> Any:
        return self.get(key, "")
    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value
    def asdict(self) -> Dict[str, Any]:
        return dict(self)

def _default_company() -> DotDict:
    return DotDict({
        "name": "",
        "industry": "",
        "size": "",
        "audience": "",
        "goals": "",
        "brand_voice": "",
    })

def init() -> None:
    """Idempotent session bootstrap."""
    ss = st.session_state
    ss.setdefault("company", _default_company())
    ss.setdefault("history", [])           # list[dict]
    # do NOT assume openai_ok; compute live in has_openai()

def get_company() -> DotDict:
    init()
    co = st.session_state.get("company")
    if isinstance(co, dict) and not isinstance(co, DotDict):
        co = DotDict(co)
        st.session_state["company"] = co
    if co is None:
        co = _default_company()
        st.session_state["company"] = co
    return co

def set_company(data: Dict[str, Any]) -> None:
    init()
    st.session_state["company"] = DotDict(data)

def has_openai() -> bool:
    """
    Truthy if a key is present in Streamlit secrets or env.
    Also caches the flag in session_state['openai_ok'] for pages that read it.
    """
    key = (
        str(st.secrets.get("openai_api_key", "")).strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )
    ok = bool(key)
    st.session_state["openai_ok"] = ok
    return ok

def get_history() -> list:
    init()
    return st.session_state["history"]
