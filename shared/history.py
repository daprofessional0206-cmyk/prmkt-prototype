# shared/history.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import streamlit as st


# ---------- Internal ----------
def _ensure_history() -> List[Dict[str, Any]]:
    if "history" not in st.session_state or not isinstance(st.session_state["history"], list):
        st.session_state["history"] = []
    return st.session_state["history"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- Public API ----------
def get_history() -> List[Dict[str, Any]]:
    """Return the session history list (never None)."""
    return list(_ensure_history())  # return a shallow copy


def clear_history() -> None:
    st.session_state["history"] = []


def add_history(
    kind: str,
    inputs: Dict[str, Any],
    outputs: Any,
    tags: Optional[List[str]] = None,
) -> None:
    """
    Append a standard history item. Keys are conservative so pages
    can safely read them without KeyErrors.
    """
    hist = _ensure_history()
    entry: Dict[str, Any] = {
        "ts": _now_iso(),
        "kind": str(kind),
        "inputs": inputs or {},
        "outputs": outputs,
        "tags": list(tags) if tags else [],
    }
    hist.append(entry)


def filtered(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    search: str = "",
) -> List[Dict[str, Any]]:
    """
    Filter history in-memory by kind, tags and free-text search
    (searches inputs/outputs stringified).
    """
    data = _ensure_history()
    if not data:
        return []

    kinds_set = {k.lower() for k in (kinds or [])}
    tags_set = {t.lower() for t in (tags or [])}
    s = (search or "").lower().strip()

    def _match(item: Dict[str, Any]) -> bool:
        if kinds_set:
            if item.get("kind", "").lower() not in kinds_set:
                return False
        if tags_set:
            item_tags = {str(t).lower() for t in item.get("tags", [])}
            if not (item_tags & tags_set):
                return False
        if s:
            blob = (json.dumps(item.get("inputs", {}), ensure_ascii=False) + " " +
                    json.dumps(item.get("outputs", {}), ensure_ascii=False)).lower()
            if s not in blob:
                return False
        return True

    return [it for it in data if _match(it)]


# --- Import / Export helpers used by the History page ---

def to_json() -> str:
    """Return the whole history as a JSON string."""
    return json.dumps(_ensure_history(), ensure_ascii=False, indent=2)


def from_json(text_or_bytes: Any) -> int:
    """
    Load items from a JSON string/bytes and append to history.
    Returns the number of items appended. Skips invalid rows.
    """
    if text_or_bytes is None:
        return 0

    try:
        if isinstance(text_or_bytes, (bytes, bytearray)):
            payload = json.loads(text_or_bytes.decode("utf-8", errors="ignore"))
        elif isinstance(text_or_bytes, str):
            payload = json.loads(text_or_bytes)
        else:
            # Try Streamlit UploadedFile
            try:
                payload = json.loads(text_or_bytes.getvalue().decode("utf-8", errors="ignore"))  # type: ignore[attr-defined]
            except Exception:
                return 0
    except Exception:
        return 0

    if not isinstance(payload, list):
        return 0

    added = 0
    hist = _ensure_history()
    for row in payload:
        if not isinstance(row, dict):
            continue
        # normalize keys we actually use
        hist.append({
            "ts": row.get("ts") or _now_iso(),
            "kind": row.get("kind", "unknown"),
            "inputs": row.get("inputs", {}),
            "outputs": row.get("outputs", {}),
            "tags": row.get("tags", []),
        })
        added += 1
    return added
