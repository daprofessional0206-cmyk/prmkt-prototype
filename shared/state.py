# shared/state.py
from __future__ import annotations
import streamlit as st
from typing import Any, Dict

# ---- Compat shim: Streamlit renamed experimental_rerun -> rerun ----
# If any page still calls st.experimental_rerun, keep it working.
if not hasattr(st, "experimental_rerun"):
    st.experimental_rerun = st.rerun  # type: ignore[attr-defined]

class DotDict(dict):
    """
    Dict that also allows attribute access (obj.key) and safe missing keys.
    Also provides .asdict() for callers that expect dataclasses.asdict().
    """
    def __getattr__(self, key: str) -> Any:
        return self.get(key, "")
    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value
    def asdict(self) -> Dict[str, Any]:  # dataclass-like
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
    ss.setdefault("openai_ok", False)
    ss.setdefault("history", [])  # list of dicts; used by shared.history

def get_company() -> DotDict:
    """Return a DotDict so pages can use co['x'] or co.x interchangeably."""
    init()
    co = st.session_state.get("company")
    # If something overwrote it with a plain dict, wrap again:
    if isinstance(co, dict) and not isinstance(co, DotDict):
        co = DotDict(co)
        st.session_state["company"] = co
    if co is None:
        co = _default_company()
        st.session_state["company"] = co
    return co  # DotDict

def set_company(data: Dict[str, Any]) -> None:
    init()
    st.session_state["company"] = DotDict(data)

def has_openai() -> bool:
    init()
    return bool(st.session_state.get("openai_ok", False))

def set_openai_ready(ok: bool) -> None:
    init()
    st.session_state["openai_ok"] = bool(ok)

def get_history() -> list:
    init()
    return st.session_state["history"]
