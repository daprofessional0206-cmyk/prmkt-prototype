from __future__ import annotations

import streamlit as st
from shared import state
from shared.history import add_history

# Try to import feedparser but don't crash if it's missing
FEED_OK = True
FEED_ERR = ""
try:
    import feedparser  # type: ignore
except Exception as e:  # ImportError or anything else
    FEED_OK = False
    FEED_ERR = str(e)

st.set_page_config(page_title="Media Monitor", page_icon="📡", layout="wide")
st.title("📡 Media Monitor (v1)")
st.caption("Paste RSS/Atom feeds (newsrooms, PR wires, blogs). Filter by keywords. Click **Check now** to pull latest.")

state.init()

default_feeds = (
    "https://news.google.com/rss\n"
    "https://feeds.feedburner.com/Techcrunch\n"
)

urls = st.text_area("Feed URLs (one per line)", value=default_feeds, height=120)
keywords = st.text_input("Filter keywords (comma-separated)", value="")
limit = st.slider("Max items per feed", 3, 20, 5)

col_a, col_b = st.columns([1, 1])
with col_a:
    do = st.button("Check now", type="primary", disabled=not FEED_OK)
with col_b:
    if st.button("Clear Output"):
        st.session_state.pop("monitor_md", None)
        st.rerun()

if not FEED_OK:
    st.error(
        "The optional dependency **feedparser** is not available, so the checker is disabled.\n\n"
        "Install it locally with `pip install feedparser` and ensure `requirements.txt` "
        "contains `feedparser>=6.0.10`. Then redeploy."
    )

if do and FEED_OK:
    keys = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    lines: list[str] = []
    for raw in urls.splitlines():
        u = raw.strip()
        if not u:
            continue
        try:
            feed = feedparser.parse(u)
            title = getattr(feed, "feed", {}).get("title", u)
            lines.append(f"\n### {title}\n")
            shown = 0
            for entry in getattr(feed, "entries", []):
                text = f"{entry.get('title','')}\n{entry.get('summary','')}"
                if keys and not any(k in text.lower() for k in keys):
                    continue
                link = entry.get("link", "")
                item_title = entry.get("title", "(no title)")
                lines.append(f"- [{item_title}]({link})")
                shown += 1
                if shown >= limit:
                    break
        except Exception as e:
            lines.append(f"- *(error parsing {u}: {e})*")

    md = "\n".join(lines) if lines else "_No items found._"
    st.session_state["monitor_md"] = md
    add_history("monitor", {"keywords": keywords, "limit": limit}, md, tags=["monitor"])

st.markdown(st.session_state.get("monitor_md", ""))

st.info(
    "To make this automatic later: run a small cron/worker that fetches feeds and writes "
    "results to your history store (Phase 4)."
)
