# shared/history.py
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import streamlit as st


# ---------- internal ---------------------------------------------------------
def _store() -> List[Dict[str, Any]]:
    """Return the in-session history list, creating it if missing."""
    return st.session_state.setdefault("history", [])


# ---------- write ------------------------------------------------------------
def add_history(
    kind: str,
    payload: Dict[str, Any],
    result: Any,
    tags: Optional[List[str]] = None,
) -> None:
    """
    Append a history item to session state.
    - kind: short type like "variants", "strategy", "test"
    - payload: inputs used to generate the result
    - result: the generated output (text, dict, list...)
    - tags: optional list of strings for filtering (e.g., ["press_release","English"])
    """
    item: Dict[str, Any] = {
        "kind": kind,
        "payload": payload,
        "result": result,
        "tags": tags or [],
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    # newest first
    _store().insert(0, item)


# Backward-compat for older pages that did: from shared.history import add
add = add_history  # noqa: N816


# ---------- read / query -----------------------------------------------------
def get_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Return most recent items (default 20)."""
    return _store()[:limit]


def clear_history() -> None:
    """Remove all items."""
    st.session_state["history"] = []


def filter_options() -> Tuple[List[str], List[str]]:
    """
    Return (kinds, tags) seen in history for populating select widgets.
    """
    kinds = sorted({it.get("kind", "") for it in _store() if it.get("kind")})
    tags = sorted({t for it in _store() for t in it.get("tags", [])})
    return kinds, tags


def filtered(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    search: str = "",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Filter history by kinds, tags and free-text search.
    """
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


# ---------- import / export --------------------------------------------------
def export_json() -> str:
    """Return the whole history as a pretty JSON string."""
    return json.dumps(_store(), ensure_ascii=False, indent=2)


def import_json(text: str) -> Tuple[bool, str]:
    """
    Merge items from a JSON string (list of dicts) into history.
    Returns (ok, message).
    """
    try:
        data = json.loads(text)
        if isinstance(data, list):
            # prepend imported items so they appear first
            st.session_state["history"] = list(data) + _store()
            return True, f"Imported {len(data)} item(s)."
        return False, "JSON root must be a list."
    except Exception as e:
        return False, f"Invalid JSON: {e}"
