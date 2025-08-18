# shared/history.py
from __future__ import annotations

import streamlit as st
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


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
    The structure matches what the History page expects.
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
    # keep only last 20
    del h[20:]


# Optional helpers used by the History page (export/import)
def export_history_json() -> str:
    import json

    return json.dumps(get_history(), ensure_ascii=False, indent=2)


def import_history_json(text: str) -> None:
    import json

    data = json.loads(text)
    if isinstance(data, list):
        st.session_state["history"] = data[:20]
    else:
        raise ValueError("History JSON must be a list.")
