# pages/05_History_Insights.py
from __future__ import annotations
import streamlit as st
import json
from typing import List
from shared.history import get_history, filter_history, export_history_json, import_history_json

st.title("History (last 20)")

items = get_history()

# Build options safely from actual data
all_kinds = sorted({it.get("kind", "") for it in items if it.get("kind")})
all_tags  = sorted({t for it in items for t in it.get("tags", [])})

colA, colB, colC = st.columns([1.2, 1.2, 1.6])

with colA:
    selected_kinds: List[str] = st.multiselect(
        "Filter by type",
        options=all_kinds,
        default=[],                 # no invalid defaults
        key="hist_kinds",
        help="Select one or more history item types."
    )

with colB:
    selected_tags: List[str] = st.multiselect(
        "Filter by tag(s)",
        options=all_tags,
        default=[],                 # no invalid defaults
        key="hist_tags",
        help="Items must include all selected tags."
    )

with colC:
    search_text = st.text_input(
        "Search text",
        value=st.session_state.get("history_search", ""),
        key="history_search",
        placeholder="Find in input/output…"
    )

# Export / Import / Clear row
exp1, clr, imp = st.columns([1.2, 1.0, 2.2])
with exp1:
    if st.button("Export history (.json)", use_container_width=True):
        st.download_button(
            "Download history.json",
            data=export_history_json().encode("utf-8"),
            file_name="history.json",
            mime="application/json",
            use_container_width=True,
            key="btn_hist_dl"
        )

with clr:
    if st.button("🗑 Clear history", use_container_width=True):
        st.session_state["history"] = []
        st.success("History cleared.")

with imp:
    st.caption("Import history (.json)")
    up = st.file_uploader("Drag and drop or browse", type=["json"], label_visibility="collapsed")
    if up is not None:
        try:
            import_history_json(up.getvalue().decode("utf-8"))
            st.success("History imported.")
        except Exception as e:
            st.error(f"Import failed: {e}")

# Apply filters
filtered = filter_history(
    kinds=selected_kinds if selected_kinds else None,
    tags=selected_tags if selected_tags else None,
    search=search_text or ""
)

st.caption(f"Showing {len(filtered)} of {len(items)} item(s).")

if not filtered:
    st.info("No items match your filters yet.")
else:
    for idx, it in enumerate(filtered, start=1):
        with st.expander(f"{idx}. {it.get('kind', 'unknown')} · {it.get('ts','')}", expanded=False):
            st.markdown("**Tags:** " + ", ".join(it.get("tags", [])) if it.get("tags") else "_(no tags)_")
            st.markdown("**Input:**")
            st.code(json.dumps(it.get("input", {}), ensure_ascii=False, indent=2), language="json")
            st.markdown("**Output:**")
            out = it.get("output", "")
            if isinstance(out, (dict, list)):
                st.code(json.dumps(out, ensure_ascii=False, indent=2), language="json")
            else:
                st.markdown(str(out))
