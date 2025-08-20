# shared/history.py
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import io

import streamlit as st


# ---------- internal ----------
def _ensure_store() -> None:
    if "history" not in st.session_state:
        st.session_state["history"] = []  # type: ignore[assignment]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_jsonable(obj: Any) -> Any:
    """Make dataclasses JSON-friendly."""
    if is_dataclass(obj):
        return asdict(obj)
    return obj


# ---------- public API ----------
def add_history(
    kind: str,
    payload: Dict[str, Any],
    output: Any,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Append an item to session history (most-recent first).

    kind: one of "strategy", "variants", "optimizer", etc.
    payload: inputs used to generate output (safe to serialize)
    output: generated result object (dict / str / list)
    tags: optional list of strings for filtering (e.g., ["Press Release", "English"])
    """
    _ensure_store()
    item = {
        "ts": _now_iso(),
        "kind": kind,
        "payload": _to_jsonable(payload),
        "output": _to_jsonable(output),
        "tags": list(filter(None, tags or [])),
    }
    st.session_state["history"].insert(0, item)  # newest first
    return item


def get_history() -> List[Dict[str, Any]]:
    _ensure_store()
    return st.session_state["history"]  # type: ignore[return-value]


def clear_history() -> None:
    st.session_state["history"] = []


def filtered(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    search: str = "",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    items = list(get_history())
    if kinds:
        ks = set(kinds)
        items = [it for it in items if it.get("kind") in ks]
    if tags:
        tg = set(tags)
        items = [it for it in items if tg.intersection(set(it.get("tags") or []))]
    if search:
        s = search.lower().strip()
        items = [
            it
            for it in items
            if s in json.dumps(it.get("payload", {})).lower()
            or s in json.dumps(it.get("output", {})).lower()
        ]
    return items[:limit]


# ----- import/export (.json) -----
def export_json() -> bytes:
    return json.dumps(get_history(), ensure_ascii=False, indent=2).encode("utf-8")


def import_json_file(file) -> int:
    """
    Accepts a file-like from st.file_uploader. Returns appended count.
    """
    try:
        content = file.read()
        data = json.loads(content.decode("utf-8"))
        if not isinstance(data, list):
            return 0
        _ensure_store()
        before = len(st.session_state["history"])
        # newest-first: bring imported items to the top, in their listed order
        for it in reversed(data):
            st.session_state["history"].insert(0, it)
        return len(st.session_state["history"]) - before
    except Exception:
        return 0
# shared/history.py
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import io

import streamlit as st


# ---------- internal ----------
def _ensure_store() -> None:
    if "history" not in st.session_state:
        st.session_state["history"] = []  # type: ignore[assignment]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_jsonable(obj: Any) -> Any:
    """Make dataclasses JSON-friendly."""
    if is_dataclass(obj):
        return asdict(obj)
    return obj


# ---------- public API ----------
def add_history(
    kind: str,
    payload: Dict[str, Any],
    output: Any,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Append an item to session history (most-recent first).

    kind: one of "strategy", "variants", "optimizer", etc.
    payload: inputs used to generate output (safe to serialize)
    output: generated result object (dict / str / list)
    tags: optional list of strings for filtering (e.g., ["Press Release", "English"])
    """
    _ensure_store()
    item = {
        "ts": _now_iso(),
        "kind": kind,
        "payload": _to_jsonable(payload),
        "output": _to_jsonable(output),
        "tags": list(filter(None, tags or [])),
    }
    st.session_state["history"].insert(0, item)  # newest first
    return item


def get_history() -> List[Dict[str, Any]]:
    _ensure_store()
    return st.session_state["history"]  # type: ignore[return-value]


def clear_history() -> None:
    st.session_state["history"] = []


def filtered(
    kinds: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    search: str = "",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    items = list(get_history())
    if kinds:
        ks = set(kinds)
        items = [it for it in items if it.get("kind") in ks]
    if tags:
        tg = set(tags)
        items = [it for it in items if tg.intersection(set(it.get("tags") or []))]
    if search:
        s = search.lower().strip()
        items = [
            it
            for it in items
            if s in json.dumps(it.get("payload", {})).lower()
            or s in json.dumps(it.get("output", {})).lower()
        ]
    return items[:limit]


# ----- import/export (.json) -----
def export_json() -> bytes:
    return json.dumps(get_history(), ensure_ascii=False, indent=2).encode("utf-8")


def import_json_file(file) -> int:
    """
    Accepts a file-like from st.file_uploader. Returns appended count.
    """
    try:
        content = file.read()
        data = json.loads(content.decode("utf-8"))
        if not isinstance(data, list):
            return 0
        _ensure_store()
        before = len(st.session_state["history"])
        # newest-first: bring imported items to the top, in their listed order
        for it in reversed(data):
            st.session_state["history"].insert(0, it)
        return len(st.session_state["history"]) - before
    except Exception:
        return 0
