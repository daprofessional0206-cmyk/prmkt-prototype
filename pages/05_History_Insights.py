# pages/05_History_Insights.py
from __future__ import annotations
import streamlit as st
import pandas as pd
from shared import ui, history

ui.page_title("History & Insights", "Browse, filter, export/import your work.")

data = history.get_history()
if not data:
    st.info("No history yet. Generate something in Strategy or Content Engine.")
    st.stop()

df = pd.DataFrame(data)
df["ts"] = pd.to_datetime(df["ts"])

kinds = sorted(df["kind"].unique().tolist())
sel_kinds = st.multiselect("Filter by kind", kinds, default=kinds)
show = df[df["kind"].isin(sel_kinds)].copy()

def preview_payload(p):
    try:
        if isinstance(p, dict):
            keys = ", ".join(list(p.keys())[:4])
            return f"{{{keys}...}}"
        return ""
    except Exception:
        return ""

show = show[["ts","kind","text","payload","tags","meta"]].copy()
show["payload"] = show["payload"].apply(preview_payload)

st.dataframe(show, use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.download_button("Download JSON", data=history.export_json_str().encode("utf-8"),
                       file_name="history.json", mime="application/json")
with c2:
    uploaded = st.file_uploader("Import JSON", type=["json"])
    if uploaded is not None:
        history.import_json_str(uploaded.getvalue().decode("utf-8"))
        st.success("Imported — reload page to see updates.")
with c3:
    if st.button("Clear history", type="primary"):
        st.session_state["history"] = []
        st.success("Cleared — reload page.")
