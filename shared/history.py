# shared/history.py
from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, cast

import streamlit as st
import pandas as pd

def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def _ensure() -> None:
    if "history" not in st.session_state:
        st.session_state["history"] = cast(List[Dict[str, Any]], [])

# ---- API expected by pages ---------------------------------------------------

def get_history() -> List[Dict[str, Any]]:
    """Return the full in-memory history list (newest first)."""
    _ensure()
    return st.session_state["history"]

def add_history(
    item_type: str,
    payload: Optional[Dict[str, Any]] = None,
    output: Optional[Any] = None,
    tags: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> None:
    """
    Flexible logger. Works with old and new call styles:
      add_history(type, payload, output, tags=[...])
      add_history(type, input={...}, result=..., tags=[...])
    """
    _ensure()
    if payload is None:
        payload = kwargs.get("input") or kwargs.get("data") or {}
    if output is None:
        output  = kwargs.get("result") or kwargs.get("content") or kwargs.get("text")

    row = {
        "ts": _now_iso(),
        "type": item_type,
        "payload": payload or {},
        "output": output if output is not None else "",
        "tags": list(tags) if tags else [],
    }
    st.session_state["history"].insert(0, row)  # newest first

def export_json() -> str:
    _ensure()
    return json.dumps(st.session_state["history"], ensure_ascii=False, indent=2)

def clear() -> None:
    _ensure()
    st.session_state["history"].clear()

def last_n(n: int = 20) -> List[Dict[str, Any]]:
    _ensure()
    return st.session_state["history"][:n]

def dataframe(limit: int = 20) -> pd.DataFrame:
    _ensure()
    rows = last_n(limit)
    if not rows:
        return pd.DataFrame(columns=["ts", "type", "payload", "output", "tags"])
    return pd.DataFrame(rows)
