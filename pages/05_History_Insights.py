# pages/05_History_Insights.py
from __future__ import annotations
import streamlit as st
import pandas as pd
from shared import history

st.set_page_config(page_title="History & Insights", page_icon="📊", layout="wide")
st.title("📊 History & Insights")

df = history.get()
if df.empty:
    st.info("No history yet. Generate something in Strategy or Content Engine.")
else:
    st.caption(f"{len(df)} item(s)")
    # simple filters
    tools = sorted(df["tool"].dropna().unique().tolist())
    tool = st.selectbox("Filter by tool", ["(All)"] + tools, index=0)
    show = df
    if tool != "(All)":
        show = show[show["tool"] == tool]
    # table-like view
    for i, row in show.iterrows():
        with st.expander(f"{row['tool']} • {row['ts']}"):
            st.write("**Payload**")
            st.json(row["payload"])
            st.write("**Output**")
            st.write(row["output"])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Download history (.json)"):
            st.download_button(
                "Save JSON",
                data=history.export_json().encode("utf-8"),
                file_name="presence_history.json",
                mime="application/json",
            )
    with c2:
        if st.button("Clear all history"):
            history.clear()
            st.success("History cleared.")
            st.rerun()
