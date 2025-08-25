# pages/09_Media_Monitor.py
from __future__ import annotations
import streamlit as st
from shared import state, history

st.set_page_config(page_title="Media Monitor", page_icon="📰", layout="wide")
st.title("📰 Media Monitor (v1)")
st.caption("Paste RSS/Atom feed URLs; filter by keywords. (Lightweight local demo.)")

state.init()

urls = st.text_area(
    "Feed URLs (one per line)",
    value="https://news.google.com/rss",
    height=100,
)
keywords = st.text_input("Filter keywords (comma-separated)", value="")
limit = st.slider("Max items per feed", 1, 50, 10)

if st.button("Fetch", use_container_width=True):
    try:
        import feedparser  # optional, local only
    except Exception:
        st.warning("Install `feedparser` in requirements.txt for live parsing. Showing placeholder.")
        st.write("- Example Item 1: Placeholder because `feedparser` not installed.")
        st.write("- Example Item 2: Placeholder because `feedparser` not installed.")
    else:
        kws = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        for u in [u.strip() for u in urls.splitlines() if u.strip()]:
            d = feedparser.parse(u)
            st.subheader(u)
            shown = 0
            for e in d.entries:
                title = e.get("title","")
                if kws and not any(k in title.lower() for k in kws):
                    continue
                st.markdown(f"- **{title}**")
                shown += 1
                if shown >= limit:
                    break
    history.add(
        tool="Media Monitor",
        payload={"urls": urls, "keywords": keywords, "limit": limit},
        output="ok",
        tags=["media-monitor"],
        meta={},
    )
