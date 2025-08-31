# shared/history.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
import streamlit as st

# Store history in session; each item:
# { ts, kind, text, payload, tags, tool, meta }
def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def get_history() -> List[Dict[str, Any]]:
    return st.session_state.setdefault("history", [])

def add(
    *,
    kind: str,
    text: str,
    payload: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    tool: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    item = {
        "ts": _now_iso(),
        "kind": kind,
        "text": text,
        "payload": payload or {},
        "tags": tags or [],
        "tool": tool or "",
        "meta": meta or {},
    }
    hist = get_history()
    hist.insert(0, item)
    # keep last 100
    del hist[100:]

def export_json() -> str:
    import json
    return json.dumps(get_history(), ensure_ascii=False, indent=2)

def import_json(json_text: str) -> None:
    import json
    try:
        data = json.loads(json_text)
        if isinstance(data, list):
            st.session_state["history"] = data[:100]
        else:
            st.warning("History JSON must be a list.")
    except Exception as e:
        st.error(f"Failed to import history: {e}")

def filtered(kind_whitelist: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    items = list(get_history())
    if kind_whitelist:
        items = [i for i in items if i.get("kind") in set(kind_whitelist)]
    return items

def latest_by_kind(kind: str) -> Optional[Dict[str, Any]]:
    for i in get_history():
        if i.get("kind") == kind:
            return i
    return None
