# pages/05_History_Insights.py
from __future__ import annotations
import json
import time
import streamlit as st

# Try to use helpers if they exist
try:
    from shared.history import filtered, export_json, import_json, get_history, known_tags  # type: ignore
except Exception:
    def get_history():
        return st.session_state.get("history", [])
    def filtered(kinds=None, tags=None, text=None):
        data = get_history()
        kinds = kinds or []
        tags = tags or []
        text = (text or "").lower().strip()
        def ok(item):
            if kinds and item.get("kind") not in kinds: return False
            if tags and not set(tags).issubset(set(item.get("tags", []))): return False
            if text and text not in json.dumps(item).lower(): return False
            return True
        return [x for x in data if ok(x)]
    def export_json(items): 
        return json.dumps(items, ensure_ascii=False, indent=2)
    def import_json(txt):
        return json.loads(txt)
    def known_tags():  # derive from data
        seen = set()
        for it in get_history(): 
            for t in it.get("tags", []): seen.add(t)
        return sorted(seen)

st.set_page_config(page_title="History & Insights", page_icon="📜", layout="wide")
st.title("History (last 20)")

with st.expander("Export / Import"):
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Export history (.json)"):
            txt = export_json(get_history())
            st.download_button("Download history.json", txt, file_name="history.json")
    with c2:
        up = st.file_uploader("Import history (.json)", type=["json"])
        if up is not None:
            try:
                items = import_json(up.getvalue().decode("utf-8"))
                st.session_state.setdefault("history", [])
                st.session_state["history"].extend(items)
                st.success(f"Imported {len(items)} items.")
            except Exception as e:
                st.error(f"Failed to import: {e}")

# Filters
kinds = st.multiselect("Filter by type", options=["variants","strategy","ab_test"], default=[])
tags = st.multiselect("Filter by tag(s)", options=known_tags(), default=[])
search = st.text_input("Search text")

items = filtered(kinds=kinds, tags=tags, text=search)[:20]
st.write(f"Showing {len(items)} of up to 20 items.")

for i, it in enumerate(items, start=1):
    with st.expander(f"{i}. {it.get('kind','item')} • {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(it.get('ts', time.time())))}"):
        st.json(it.get("payload", {}))
        st.markdown(it.get("output", ""))
        if it.get("tags"):
            st.caption("Tags: " + ", ".join(it["tags"]))
