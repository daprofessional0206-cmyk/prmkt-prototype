# pages/05_History_Insights.py
from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import Any, Dict
from shared import history

st.set_page_config(page_title="Presence • History & Insights", page_icon="📊", layout="wide")

st.title("📊 History & Insights")
st.caption("Browse, filter, export, and learn from your past generations.")

data = history.get_history()
if not data:
    st.info("No history yet. Generate something in Strategy or Content Engine.")
else:
    # Filters
    kinds = sorted(list({d.get("kind", "") for d in data if d.get("kind")}))
    tags = sorted(list({tag for d in data for tag in (d.get("tags") or [])}))

    c1, c2 = st.columns(2)
    with c1:
        selected_kinds = st.multiselect("Filter by type", options=kinds, default=kinds)
    with c2:
        selected_tag = st.selectbox("Filter by one tag (optional)", options=["(any)"] + tags, index=0)

    show = [d for d in data if d.get("kind") in (selected_kinds or kinds)]
    if selected_tag != "(any)":
        show = [d for d in show if selected_tag in (d.get("tags") or [])]

    # Table
    def _payload_preview(p: Dict[str, Any]) -> str:
        if not isinstance(p, dict):
            return "-"
        topic = p.get("topic") or p.get("goals") or p.get("primary_channel") or p.get("content_type") or ""
        return str(topic)[:80]

    rows = []
    for it in show:
        rows.append({
            "ts": it.get("ts", ""),
            "kind": it.get("kind", ""),
            "tags": ", ".join(it.get("tags") or []),
            "payload": _payload_preview(it.get("payload", {})),
            "len(output)": (len(it.get("output")) if isinstance(it.get("output"), str) else len(it.get("output") or [])),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=380)

    st.subheader("Raw entry viewer")
    idx = st.number_input("Index (1 = latest)", min_value=1, max_value=len(show), value=1, step=1)
    item = show[int(idx) - 1]
    st.json(item)

    c3, c4 = st.columns(2)
    with c3:
        if st.button("Download history (.json)"):
            st.download_button(
                "Save JSON",
                data=history.export_json().encode("utf-8"),
                file_name="presence_history.json",
                mime="application/json",
                use_container_width=True,
            )
    with c4:
        if st.button("Clear all history"):
            history.clear()
            st.success("History cleared.")
            st.rerun()
