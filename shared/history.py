# shared/history.py
from __future__ import annotations

import streamlit as st
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_history() -> List[Dict[str, Any]]:
    """Return the session history list (create if missing)."""
    return st.session_state.setdefault("history", [])


def add_history(
    kind: str,
    payload: Dict[str, Any],
    output: Any,
    tags: Optional[List[str]] = None,
) -> None:
    """
    Insert an item at the top of history and cap at 20 items.
    Structure matches what the History page expects.
    """
    h = get_history()
    h.insert(
        0,
        {
            "ts": _now_iso(),
            "kind": kind,
            "input": payload,
            "output": output,
            "tags": tags or [],
        },
    )
    del h[20:]  # keep last 20


def export_history_json() -> str:
    return json.dumps(get_history(), ensure_ascii=False, indent=2)


def import_history_json(text: str) -> None:
    data = json.loads(text)
    if isinstance(data, list):
        st.session_state["history"] = data[:20]
    else:
        raise ValueError("History JSON must be a list.")


def filter_history(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    search: str = "",
) -> List[Dict[str, Any]]:
    """
    Small utility that filters current history in-memory:
      - kinds: list of kind names to include (e.g., ["Variants","strategy"])
      - tags:  items must include ALL provided tags
      - search: case-insensitive substring match across input/output
    """
    items = get_history()
    if kinds:
        kinds_set = {k.lower() for k in kinds}
        items = [it for it in items if it.get("kind", "").lower() in kinds_set]
    if tags:
        tags_set = {t.lower() for t in tags}
        items = [
            it
            for it in items
            if tags_set.issubset({t.lower() for t in it.get("tags", [])})
        ]
    if search:
        s = search.lower()
        def blob(x: Any) -> str:
            try:
                return json.dumps(x, ensure_ascii=False).lower()
            except Exception:
                return str(x).lower()
        items = [
            it for it in items
            if s in blob(it.get("output")) or s in blob(it.get("input"))
        ]
    return items


# ── Backward-compatibility aliases (so old imports keep working) ─────────────
add = add_history
export_json = export_history_json
import_json = import_history_json
filtered = filter_history
