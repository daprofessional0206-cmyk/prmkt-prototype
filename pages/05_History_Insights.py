import streamlit as st
from shared import history

st.set_page_config(page_title="History & Insights", page_icon="📊")

st.title("📊 History & Insights")
st.write("Review, search, and filter everything you’ve generated.")

items = history.get_history()

kind_filter = st.multiselect("Filter by type", ["Strategy", "Content", "Optimizer"])
tag_filter = st.text_input("Filter by tag (comma-separated)")
query = st.text_input("Search text")

tags = [t.strip() for t in tag_filter.split(",") if t.strip()]
filtered = history.filtered(kinds=kind_filter, tags=tags, q=query)

st.write(f"Showing {len(filtered)} items")

for it in filtered:
    st.markdown(f"**{it['kind']}** — {it['ts']}")
    if it.get("tags"):
        st.caption(", ".join(it["tags"]))
    st.json(it["input"])
    if isinstance(it["output"], list):
        for o in it["output"]:
            st.markdown(o)
            st.divider()
    else:
        st.markdown(it["output"])
    st.divider()

if st.button("🗑️ Clear All History"):
    history.clear()
    st.success("History cleared.")
