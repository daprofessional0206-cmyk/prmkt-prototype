# shared/history.py
from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import re
import streamlit as st


MAX_ITEMS = 200  # keep history light but useful


def _init() -> None:
    if "history" not in st.session_state or not isinstance(st.session_state["history"], list):
        st.session_state["history"] = []


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_history() -> List[Dict[str, Any]]:
    _init()
    return st.session_state["history"]


def add(kind: str, payload: Dict[str, Any], output: Any, tags: Optional[List[str]] = None) -> None:
    """Append an item to history."""
    _init()
    item = {
        "ts": now_iso(),
        "kind": kind,                     # e.g., "Strategy", "Content", "Optimizer"
        "tags": tags or [],               # e.g., ["content","Press Release"]
        "input": payload,                 # arbitrary dict
        "output": output,                 # str or list[str]
    }
    st.session_state["history"].insert(0, item)
    st.session_state["history"] = st.session_state["history"][:MAX_ITEMS]


def clear() -> None:
    _init()
    st.session_state["history"] = []


def export_json() -> str:
    _init()
    return json.dumps(st.session_state["history"], ensure_ascii=False, indent=2)


def import_json(text: str) -> None:
    """Replace history with a provided JSON array."""
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Imported JSON must be a list.")
    st.session_state["history"] = data[:MAX_ITEMS]


def _contains_text(obj: Any, needle: str) -> bool:
    """Recursive text search for filtering."""
    n = needle.lower()
    if obj is None:
        return False
    if isinstance(obj, (str, int, float, bool)):
        return n in str(obj).lower()
    if isinstance(obj, list):
        return any(_contains_text(x, needle) for x in obj)
    if isinstance(obj, dict):
        return any(_contains_text(v, needle) for v in obj.values())
    return False


def filtered(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    q: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter history by kinds, tags and free text query."""
    _init()
    items = st.session_state["history"]

    if kinds:
        setk = set(kinds)
        items = [it for it in items if str(it.get("kind")) in setk]

    if tags:
        sett = set(tags)
        items = [it for it in items if sett.intersection(set(it.get("tags", [])))]

    if q and q.strip():
        query = q.strip()
        items = [it for it in items if _contains_text(it, query)]

    return items
