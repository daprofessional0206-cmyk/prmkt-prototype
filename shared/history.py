# shared/history.py
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import streamlit as st
import pandas as pd

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_history() -> List[Dict[str, Any]]:
    return st.session_state.setdefault("history", [])

def clear_history() -> None:
    st.session_state["history"] = []

def add_history(kind: str, payload: Dict[str, Any], output: Any, tags: Optional[List[str]] = None) -> None:
    rec = {
        "ts": _now_iso(),
        "kind": kind,
        "payload": payload,  # <- canonical key
        "output": output,
        "tags": tags or [],
    }
    hist = get_history()
    hist.insert(0, rec)
    st.session_state["history"] = hist[:200]

def export_json() -> str:
    return json.dumps(get_history(), ensure_ascii=False, indent=2)

def import_json(text: str) -> None:
    data = json.loads(text)
    if isinstance(data, list):
        st.session_state["history"] = data[:200]
    else:
        st.warning("Import must be a JSON list; ignoring.")

def to_df() -> pd.DataFrame:
    """Return a DataFrame that always has columns: ts, kind, tags, payload, output."""
    hist = get_history()
    if not hist:
        return pd.DataFrame(columns=["ts", "kind", "tags", "payload", "output"])
    # normalize rows
    norm = []
    for it in hist:
        norm.append({
            "ts": it.get("ts", ""),
            "kind": it.get("kind", ""),
            "tags": it.get("tags", []),
            "payload": it.get("payload", it.get("input", {})),  # accept legacy 'input'
            "output": it.get("output", ""),
        })
    return pd.DataFrame(norm)
