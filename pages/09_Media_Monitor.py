from __future__ import annotations

import streamlit as st
import feedparser
from shared import state
from shared.history import add_history

st.set_page_config(page_title="Media Monitor", page_icon="📡", layout="wide")
st.title("📡 Media Monitor (v1)")
st.caption("Paste RSS/Atom feeds (newsrooms, PR wires, blogs). Filter by keywords. Click **Check now** to pull latest.")

state.init()

urls = st.text_area(
    "Feed URLs (one per line)",
    value="https://news.google.com/rss\nhttps://feeds.feedburner.com/Techcrunch\n",
    height=120,
)
keywords = st.text_input("Filter keywords (comma-separated)", value="")
limit = st.slider("Max items per feed", 3, 20, 5)

col_a, col_b = st.columns([1,1])
with col_a:
    do = st.button("Check now", type="primary")
with col_b:
    if st.button("Clear Output"):
        st.session_state.pop("monitor_md", None)
        st.rerun()

if do:
    keys = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    lines = []
    for raw in urls.splitlines():
        u = raw.strip()
        if not u:
            continue
        try:
            feed = feedparser.parse(u)
            title = feed.feed.get("title", u)
            lines.append(f"\n### {title}\n")
            shown = 0
            for entry in feed.entries:
                text = f"{entry.get('title','')}\n{entry.get('summary','')}"
                if keys and not any(k in text.lower() for k in keys):
                    continue
                link = entry.get("link","")
                lines.append(f"- [{entry.get('title','(no title)')}]({link})")
                shown += 1
                if shown >= limit:
                    break
        except Exception as e:
            lines.append(f"- *(error parsing {u}: {e})*")
    md = "\n".join(lines) if lines else "_No items found._"
    st.session_state["monitor_md"] = md
    add_history("monitor", {"keywords": keywords, "limit": limit}, md, tags=["monitor"])

st.markdown(st.session_state.get("monitor_md",""))
st.info("To make this automatic later: run a small cron (GitHub Actions / Cloud Scheduler) that calls this page or a webhook and writes results to your history store.")
