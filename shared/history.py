# shared/history.py
from __future__ import annotations
import json
import time
from typing import Any, Dict, List
import streamlit as st

_KEY = "presence_history_v1"

def _ensure() -> None:
    if _KEY not in st.session_state:
        st.session_state[_KEY] = []  # list[dict]

def add(kind: str, content: str, meta: Dict[str, Any] | None = None, tags: List[str] | None = None) -> None:
    """Append a history item."""
    _ensure()
    st.session_state[_KEY].append(
        {
            "ts": time.time(),
            "kind": kind,
            "content": content,
            "meta": meta or {},
            "tags": tags or [],
        }
    )

# for backward-compat with pages that import add_history
add_history = add

def get() -> List[Dict[str, Any]]:
    _ensure()
    return st.session_state[_KEY]

def clear() -> None:
    _ensure()
    st.session_state[_KEY] = []

def export_json() -> str:
    """Return the entire history as a UTF-8 JSON string."""
    return json.dumps(get(), ensure_ascii=False, indent=2)
