# shared/history.py
from __future__ import annotations
import streamlit as st
from typing import List, Dict, Any
from datetime import datetime, timezone
import json

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_history() -> List[Dict[str, Any]]:
    return st.session_state.setdefault("history", [])

def clear() -> None:
    st.session_state["history"] = []

def add(kind: str, payload: Dict[str, Any], output: Any, tags: List[str] | None = None) -> None:
    """Unified shape for all history entries."""
    hist = get_history()
    entry = {
        "ts": _now_iso(),
        "kind": kind,                    # e.g., "strategy", "content", "optimizer"
        "payload": payload or {},        # always a dict
        "output": output,                # string or list[str]
        "tags": tags or [],              # list of strings
    }
    hist.insert(0, entry)
    del hist[50:]  # keep it light

def export_json() -> str:
    return json.dumps(get_history(), ensure_ascii=False, indent=2)

def import_json(text: str) -> None:
    try:
        items = json.loads(text)
        if isinstance(items, list):
            st.session_state["history"] = items[:50]
        else:
            st.warning("JSON must be a list.")
    except Exception as e:
        st.error(f"Invalid JSON: {e}")

def filtered(kind: str | None = None, tag: str | None = None) -> List[Dict[str, Any]]:
    data = list(get_history())
    if kind:
        data = [d for d in data if d.get("kind") == kind]
    if tag:
        data = [d for d in data if tag in (d.get("tags") or [])]
    return data
