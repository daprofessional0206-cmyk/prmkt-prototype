from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import streamlit as st


def _store() -> List[Dict[str, Any]]:
    return st.session_state.setdefault("history", [])


def add_history(
    kind: str,
    payload: Dict[str, Any],
    result: Any,
    tags: Optional[List[str]] = None,
) -> None:
    item: Dict[str, Any] = {
        "kind": kind,
        "payload": payload,
        "result": result,
        "tags": tags or [],
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    _store().insert(0, item)


add = add_history  # backward compat


def get_history(limit: int = 20) -> List[Dict[str, Any]]:
    return _store()[:limit]


def clear_history() -> None:
    st.session_state["history"] = []


def filter_options() -> Tuple[List[str], List[str]]:
    kinds = sorted({it.get("kind", "") for it in _store() if it.get("kind")})
    tags = sorted({t for it in _store() for t in it.get("tags", [])})
    return kinds, tags


def filtered(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    search: str = "",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    items = list(_store())
    if kinds:
        items = [it for it in items if it.get("kind") in kinds]
    if tags:
        tagset = set(tags)
        items = [it for it in items if tagset.intersection(it.get("tags", []))]
    if search:
        s = search.lower()
        items = [it for it in items if s in json.dumps(it, ensure_ascii=False).lower()]
    return items[:limit]


def export_json() -> str:
    return json.dumps(_store(), ensure_ascii=False, indent=2)


def import_json(text: str):
    try:
        data = json.loads(text)
        if isinstance(data, list):
            st.session_state["history"] = list(data) + _store()
            return True, f"Imported {len(data)} item(s)."
        return False, "JSON root must be a list."
    except Exception as e:
        return False, f"Invalid JSON: {e}"

# Reusable: get latest item by type, or None if not found.
from typing import Optional, Dict, Any, List

def get_latest_by_type(type_name: str) -> Optional[Dict[str, Any]]:
    hist: List[Dict[str, Any]] = st.session_state.get("history", [])
    if not isinstance(hist, list):
        return None
    for item in reversed(hist):
        if isinstance(item, dict) and item.get("type") == type_name:
            return item
    return None
