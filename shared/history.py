from __future__ import annotations
import json
from datetime import datetime, timezone
import streamlit as st

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def add(kind: str, payload: dict, output, tags: list[str] | None = None):
    item = {"ts": _now(), "kind": kind, "input": payload, "output": output, "tags": tags or []}
    st.session_state.history.insert(0, item)
    st.session_state.history = st.session_state.history[:20]

def export_json() -> str:
    return json.dumps(st.session_state.history, ensure_ascii=False, indent=2)

def import_json(text: str):
    data = json.loads(text)
    if isinstance(data, list):
        st.session_state.history = data[:20]
    else:
        raise ValueError("History JSON must be a list")

def filtered():
    items = st.session_state.history
    kinds = st.session_state.history_filter_kind or []
    tags = st.session_state.history_filter_tags or []
    q = (st.session_state.history_search or "").strip().lower()

    def ok(it):
        if kinds and it.get("kind") not in kinds: return False
        if tags and not set(tags).issubset(set(it.get("tags", []))): return False
        if q:
            if q not in json.dumps(it, ensure_ascii=False).lower(): return False
        return True

    return [it for it in items if ok(it)]
