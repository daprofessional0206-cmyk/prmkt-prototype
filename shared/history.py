# shared/history.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import time
import pandas as pd
import streamlit as st

_KEY = "history"

def _ensure() -> None:
    if _KEY not in st.session_state:
        st.session_state[_KEY] = []  # newest first

def add(
    tool: str,
    payload: Dict[str, Any],
    output: Any,
    tags: Optional[List[str]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    _ensure()
    st.session_state[_KEY].insert(0, {
        "ts": int(time.time()),
        "tool": tool,
        "payload": payload,
        "output": output,
        "tags": tags or [],
        "meta": meta or {},
    })

def get() -> pd.DataFrame:
    _ensure()
    items = st.session_state[_KEY]
    if not items:
        return pd.DataFrame(columns=["ts", "tool", "payload", "output", "tags", "meta"])
    return pd.DataFrame(items)

def clear() -> None:
    _ensure()
    st.session_state[_KEY] = []

def count() -> int:
    _ensure()
    return len(st.session_state[_KEY])

def export_json(pretty: bool = True) -> str:
    _ensure()
    return json.dumps(st.session_state[_KEY], indent=2 if pretty else None, ensure_ascii=False)
