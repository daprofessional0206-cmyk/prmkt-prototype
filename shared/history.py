# shared/history.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import streamlit as st


def _ensure_state_list(name: str) -> List[Dict[str, Any]]:
    """Ensure st.session_state[name] is a list and return it."""
    if name not in st.session_state or not isinstance(st.session_state[name], list):
        st.session_state[name] = []
    return st.session_state[name]


def get_history() -> List[Dict[str, Any]]:
    """Return the in-session history list (never None)."""
    return _ensure_state_list("history")


def clear_history() -> None:
    """Clear the in-session history."""
    st.session_state["history"] = []


def _normalized_item(
    *,
    kind: str,
    payload: Dict[str, Any] | None,
    output: Any = None,
    tags: Optional[List[str]] = None,
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Produce a consistent history item schema.

    Fields:
      - kind: str            (e.g., "Variants", "strategy", "optimizer")
      - payload: dict        (inputs/UI selections)
      - output: Any          (model result, list, etc.)
      - tags: List[str]      (optional labels)
      - created_at: ISO-8601 UTC string
    """
    return {
        "kind": kind or "unknown",
        "payload": payload or {},
        "output": output,
        "tags": tags or [],
        "created_at": created_at or datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def add(
    *,
    kind: str,
    payload: Dict[str, Any] | None,
    output: Any = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Append a normalized item to history and return it.
    """
    item = _normalized_item(kind=kind, payload=payload, output=output, tags=tags)
    get_history().insert(0, item)  # newest first
    return item


# -------- Filtering / utility helpers (optional; safe if unused) --------

def filter_by_kind(items: List[Dict[str, Any]], kinds: List[str]) -> List[Dict[str, Any]]:
    if not kinds:
        return items
    want = {k.lower() for k in kinds}
    return [it for it in items if str(it.get("kind", "")).lower() in want]


def filter_by_tags(items: List[Dict[str, Any]], tags: List[str]) -> List[Dict[str, Any]]:
    if not tags:
        return items
    want = {t.lower() for t in tags}
    out: List[Dict[str, Any]] = []
    for it in items:
        its = {str(t).lower() for t in it.get("tags", [])}
        if want & its:
            out.append(it)
    return out


def search_text(items: List[Dict[str, Any]], q: str) -> List[Dict[str, Any]]:
    if not q:
        return items
    ql = q.lower()
    out = []
    for it in items:
        blob = f"{it.get('kind','')} {it.get('tags',[])} {it.get('payload',{})} {it.get('output','')}"
        if ql in blob.lower():
            out.append(it)
    return out
