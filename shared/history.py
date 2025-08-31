# shared/history.py
from __future__ import annotations
import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List
import json

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_history() -> List[Dict[str, Any]]:
    return st.session_state.setdefault("history", [])

def add(kind: str, text: str, payload: Dict[str, Any] | None = None,
        tags: List[str] | None = None, meta: Dict[str, Any] | None = None) -> None:
    item = {
        "ts": _now(),
        "kind": kind,
        "text": text,
        "payload": payload or {},
        "tags": tags or [],
        "meta": meta or {},
    }
    hist = get_history()
    hist.insert(0, item)
    del hist[200:]  # keep last 200

def export_json_str() -> str:
    return json.dumps(get_history(), ensure_ascii=False, indent=2)

def import_json_str(blob: str) -> None:
    try:
        items = json.loads(blob)
        if isinstance(items, list):
            st.session_state["history"] = items[:200]
    except Exception:
        pass

def latest_by_kind(kind: str) -> Dict[str, Any] | None:
    for it in get_history():
        if it.get("kind") == kind:
            return it
    return None
