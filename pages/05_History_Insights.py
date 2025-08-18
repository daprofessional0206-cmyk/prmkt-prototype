# pages/05_History_Insights.py
from __future__ import annotations
import streamlit as st
from shared import state, ui
from shared.history import export_json, import_json, filtered

state.init()
ui.title("History & Insights")

kinds = st.multiselect("Filter by type", ["Variants","Strategy","Optimizer","Testing"],
                       default=state.st.session_state.get("history_filter_kind", ["Variants"]))
state.st.session_state["history_filter_kind"] = kinds

tags = st.multiselect("Filter by tag(s)", options=[], default=state.st.session_state.get("history_filter_tags", []))
state.st.session_state["history_filter_tags"] = tags

search = st.text_input("Search text", value=state.st.session_state.get("history_search", ""))
state.st.session_state["history_search"] = search

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Export history (.json)"):
        st.download_button("Download", data=export_json().encode("utf-8"),
                           file_name="history.json", mime="application/json")
with col2:
    uploaded = st.file_uploader("Import history (.json)", type=["json"])
    if uploaded is not None:
        try:
            import_json(uploaded.read().decode("utf-8"))
            st.success("Imported.")
        except Exception as e:
            st.error(str(e))

ui.divider()

items = filtered()
st.caption(f"Showing {len(items)} item(s).")
for i, item in enumerate(items, 1):
    with st.expander(f"{i}. {item['kind']} • {item['ts']}"):
        st.json(item["input"])
        st.write(item["output"])
