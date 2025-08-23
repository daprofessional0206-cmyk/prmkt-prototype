from __future__ import annotations
import io
import json
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# We only READ history via helper you already have.
# No changes to shared/history.py expected.
try:
    from shared.history import get_history  # type: ignore
except Exception:  # very defensive fallback
    def get_history() -> List[Dict[str, Any]]:
        return st.session_state.get("history", [])

st.set_page_config(page_title="History & Insights", page_icon="📒", layout="wide")

st.title("📒 History & Insights")

# ---------- Load & normalize ----------
raw = get_history() or []
def _normalize_row(it: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ts": it.get("ts") or it.get("time") or "",
        "type": it.get("type") or it.get("kind") or "unknown",
        "tags": it.get("tags") or [],
        "payload": it.get("payload") or {},
        "output": it.get("output") or it.get("result") or it.get("text") or "",
    }

rows = [_normalize_row(it) for it in raw]
df = pd.DataFrame(rows)

# Make safe columns
if "tags" not in df.columns:
    df["tags"] = [[] for _ in range(len(df))]
if "type" not in df.columns:
    df["type"] = "unknown"
if "ts" not in df.columns:
    df["ts"] = ""

# Recent first if timestamps look sortable
with pd.option_context("mode.chained_assignment", None):
    try:
        df["ts_parsed"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts_parsed", ascending=False)
    except Exception:
        df["ts_parsed"] = pd.NaT

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
types = sorted(df["type"].dropna().unique().tolist()) if not df.empty else []
sel_types = st.sidebar.multiselect("Type", options=types, default=types)

# collect all tags
all_tags = sorted({t for sub in df["tags"].tolist() for t in (sub or [])})
sel_tags = st.sidebar.multiselect("Tag(s)", options=all_tags, default=[])

query = st.sidebar.text_input("Search text", value="", placeholder="Search in payload or output…")

limit = st.sidebar.slider("Rows to display", min_value=20, max_value=500, value=100, step=20)

# ---------- Apply filters ----------
f = df.copy()
if sel_types:
    f = f[f["type"].isin(sel_types)]
if sel_tags:
    f = f[f["tags"].apply(lambda ts: any(t in (ts or []) for t in sel_tags))]
if query.strip():
    q = query.lower()
    def _hit(row: pd.Series) -> bool:
        try:
            payload_txt = json.dumps(row["payload"], ensure_ascii=False)
        except Exception:
            payload_txt = str(row["payload"])
        out_txt = str(row["output"])
        return (q in payload_txt.lower()) or (q in out_txt.lower())
    f = f[f.apply(_hit, axis=1)]

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
total_items = len(df)
with c1: st.metric("Total items", f"{total_items:,}")
with c2: st.metric("After filters", f"{len(f):,}")
with c3:
    most_common_type = (
        df["type"].value_counts().idxmax() if not df.empty else "—"
    )
    st.metric("Top type", most_common_type)
with c4:
    top_tag = "—"
    if all_tags:
        # frequency across all items (not just filtered)
        freq = {}
        for ts in df["tags"]:
            for t in (ts or []):
                freq[t] = freq.get(t, 0) + 1
        top_tag = max(freq, key=freq.get) if freq else "—"
    st.metric("Top tag", top_tag)

st.divider()

# ---------- Charts ----------
cc1, cc2 = st.columns(2)
with cc1:
    st.subheader("By type")
    if not df.empty:
        st.bar_chart(df["type"].value_counts())
    else:
        st.caption("No data yet.")

with cc2:
    st.subheader("Top tags")
    if all_tags:
        tag_counts = {}
        for ts in df["tags"]:
            for t in (ts or []):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        tag_df = pd.DataFrame(
            sorted(tag_counts.items(), key=lambda x: x[1], reverse=True),
            columns=["tag", "count"]
        ).head(20)
        st.bar_chart(tag_df.set_index("tag"))
    else:
        st.caption("No tags yet.")

st.divider()

# ---------- Table ----------
st.subheader("Recent items")
show = f.head(limit).copy()

# Pretty columns
def _payload_preview(p: Any) -> str:
    try:
        s = json.dumps(p, ensure_ascii=False, indent=0)
    except Exception:
        s = str(p)
    return (s[:220] + "…") if len(s) > 220 else s

def _output_preview(o: Any) -> str:
    s = str(o)
    return (s[:280] + "…") if len(s) > 280 else s

tbl = pd.DataFrame({
    "time": show["ts"],
    "type": show["type"],
    "tags": show["tags"].apply(lambda t: ", ".join(t) if t else ""),
    "payload": show["payload"].apply(_payload_preview),
    "output": show["output"].apply(_output_preview),
})

st.dataframe(tbl, use_container_width=True, height=420)

# ---------- Export / Download ----------
exp_c1, exp_c2, exp_c3 = st.columns(3)
with exp_c1:
    if st.button("Download filtered (.jsonl)"):
        # JSON Lines of the filtered rows, raw shape
        buf = io.StringIO()
        for _, r in f.iterrows():
            j = {
                "ts": r["ts"],
                "type": r["type"],
                "tags": r["tags"],
                "payload": r["payload"],
                "output": r["output"],
            }
            buf.write(json.dumps(j, ensure_ascii=False) + "\n")
        st.download_button(
            "Save .jsonl",
            data=buf.getvalue().encode("utf-8"),
            file_name="history_filtered.jsonl",
            mime="application/json",
        )

with exp_c2:
    if st.button("Download filtered (.csv)"):
        # A compact CSV
        csv_df = pd.DataFrame({
            "ts": f["ts"],
            "type": f["type"],
            "tags": f["tags"].apply(lambda t: "|".join(t) if t else ""),
            "payload": f["payload"].apply(lambda x: json.dumps(x, ensure_ascii=False)),
            "output": f["output"],
        })
        st.download_button(
            "Save .csv",
            data=csv_df.to_csv(index=False).encode("utf-8"),
            file_name="history_filtered.csv",
            mime="text/csv",
        )

with exp_c3:
    if st.button("Copy sample row to clipboard"):
        if not f.empty:
            sample = f.iloc[0][["type", "tags", "payload", "output"]].to_dict()
            st.code(json.dumps(sample, ensure_ascii=False, indent=2))
            st.caption("Copy from the code block above.")
        else:
            st.caption("Nothing to copy; filtered set is empty.")
