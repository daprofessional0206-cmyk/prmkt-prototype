from __future__ import annotations
import streamlit as st
from shared import ui, history

# ── Sidebar health badge (safe) ───────────────────────────────────────────────
import streamlit as st
try:
    from shared import state
    with st.sidebar:
        st.write(f"OpenAI: {'✅ Connected' if state.has_openai() else '❌ Missing'}")
except Exception:
    # Never crash the page if the helper isn't available
    with st.sidebar:
        st.write("OpenAI: status unavailable")

st.set_page_config(page_title="History & Insights", page_icon="📊", layout="wide")
ui.inject_css()
ui.page_title("History (last 20)")

with st.expander("Export / Import", expanded=True):
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Export history (.json)"):
            st.download_button("Download", data=history.export_json(), file_name="history.json", mime="application/json")
        if st.button("Clear history", type="secondary"):
            history.clear_history()
            st.success("History cleared.")
    with c2:
        uploaded = st.file_uploader("Import history (.json)", type=["json"])
        if uploaded is not None:
            ok, msg = history.import_json(uploaded.read().decode("utf-8"))
            (st.success if ok else st.error)(msg)

kinds, tag_opts = history.filter_options()
kind_sel = st.multiselect("Filter by type", kinds, default=[])
tag_sel = st.multiselect("Filter by tag(s)", tag_opts, default=[])
query = st.text_input("Search text")

items = history.filtered(kind_sel, tag_sel, query, limit=20)
st.caption(f"Showing {len(items)} of up to 20 items.")
for it in items:
    with st.expander(f"{it['ts']} · {it.get('kind','—')} · {', '.join(it.get('tags',[]))}"):
        st.json(it["payload"])
        st.write(it["result"])
# ── Footer ────────────────────────────────────────────────────────────────────
import streamlit as st  # safe if already imported
st.caption("Presence — multi-page prototype (Phase 3.2 • build v3.2)")
