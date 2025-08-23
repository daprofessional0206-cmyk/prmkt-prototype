# pages/10_Campaign_Brief.py
from __future__ import annotations

import io
import json
from datetime import datetime

import streamlit as st

# Try to use your shared helpers if present, but fall back gracefully.
try:
    from shared import state  # type: ignore
except Exception:  # pragma: no cover
    state = None  # fallback later

st.set_page_config(page_title="Campaign Brief", page_icon="🗂️", layout="wide")

# ---------- Lightweight helpers (no patches to other files) ------------------


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _get_company() -> dict:
    """
    Reads the company object from shared.state (if available) or session_state.
    Returns a simple dict for templating.
    """
    # shared.state path
    if state:
        try:
            co = state.get_company()  # dataclass or dict
            # Try dataclass .__dict__ or asdict()
            if hasattr(co, "asdict"):
                return co.asdict()  # type: ignore[attr-defined]
            if hasattr(co, "__dict__"):
                return dict(co.__dict__)  # type: ignore
            if isinstance(co, dict):
                return co
        except Exception:
            pass

    # session fallback
    co = st.session_state.get("company", {})
    if hasattr(co, "__dict__"):
        co = dict(co.__dict__)  # type: ignore
    if not isinstance(co, dict):
        co = {}
    # normalize keys
    return {
        "name": co.get("name", ""),
        "industry": co.get("industry", ""),
        "size": co.get("size", ""),
        "audience": co.get("audience", ""),
        "goals": co.get("goals", ""),
        "brand_rules": co.get("brand_rules", ""),
        "voice": co.get("voice", ""),
        "website": co.get("website", ""),
    }


def _get_history() -> list[dict]:
    """
    History structure is assumed to be a list of dicts with at least:
    - type: str
    - payload / result (free-form)
    We don’t enforce a schema; we just try to present something sensible.
    """
    hist = st.session_state.get("history", [])
    if isinstance(hist, list):
        return hist
    return []


def _latest_by_type(type_name: str) -> dict | None:
    for item in reversed(_get_history()):
        if item.get("type") == type_name:
            return item
    return None


def _safe_text(obj, default: str = "") -> str:
    if obj is None:
        return default
    if isinstance(obj, (str, int, float)):
        return str(obj)
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return default


def _content_from_item(item: dict | None) -> str:
    """
    Pulls a human-readable body from a history item. Tries result, then payload,
    then the whole item as JSON.
    """
    if not item:
        return ""
    for key in ("result", "output", "text", "content", "variants"):
        val = item.get(key)
        if val:
            return _safe_text(val)
    # payload often has the prompt. Include both.
    payload_txt = _safe_text(item.get("payload", {}))
    return payload_txt or _safe_text(item)


def _make_markdown_brief() -> str:
    co = _get_company()
    strategy = _latest_by_type("strategy")
    content_variants = _latest_by_type("variants")  # Content Engine
    optimizer = _latest_by_type("optimizer") or _latest_by_type("word_optimizer")

    strategy_txt = _content_from_item(strategy)
    variants_txt = _content_from_item(content_variants)
    optimizer_txt = _content_from_item(optimizer)

    created = _now_iso()

    md = f"""# Campaign Brief — {co.get('name','')}

**Generated:** {created}

---

## 1) Company Snapshot
- **Name:** {co.get('name','')}
- **Industry:** {co.get('industry','')}
- **Size:** {co.get('size','')}
- **Audience:** {co.get('audience','')}
- **Goals:** {co.get('goals','')}
- **Voice/Brand rules:** {co.get('voice','') or co.get('brand_rules','')}
- **Website:** {co.get('website','')}

---

## 2) Strategy Idea (latest)
{strategy_txt or '_No strategy idea found in history yet._'}

---

## 3) Content Draft(s) (latest from Content Engine)
{variants_txt or '_No content variants found in history yet._'}

---

## 4) Optimization Suggestions (latest from Word Optimizer)
{optimizer_txt or '_No optimizer suggestions found in history yet._'}

---

## 5) Next Steps (suggested)
- Select one strategy angle and one draft variant.
- Apply any high-impact optimizer suggestions.
- Define channel plan (press release, landing page, email, social).
- Prepare media list (journalists & outlets) and send.
- Track performance and log to **History & Insights**.

*Presence — PR & Marketing OS*
"""
    return md


def _bytes_filenamepair_from_md(md: str, base: str = "campaign_brief") -> tuple[bytes, str]:
    return md.encode("utf-8"), f"{base}.md"


def _fake_pdf_from_md(md: str, base: str = "campaign_brief") -> tuple[bytes, str]:
    """
    Demo-only: we just wrap the markdown in a tiny text-based PDF-ish stub so a file
    downloads as .pdf. For proper PDFs we’ll add a real generator in Phase 4.
    """
    stub = f"""%PDF-1.4
% Demo-only export from Presence
% This file contains Markdown content, not a true PDF layout.
% Open with any text editor or import into a docs tool.

{md}
%%EOF
"""
    return stub.encode("utf-8"), f"{base}.pdf"


# ------------------------------- UI ------------------------------------------

st.title("🗂️ Campaign Brief")
st.caption("Bundle your latest Strategy + Draft + Optimizer into a single brief, then export or share (mock).")

left, right = st.columns([3, 2])

with left:
    st.subheader("Brief Preview")
    md = _make_markdown_brief()
    st.markdown(md)

with right:
    st.subheader("Export")

    md_bytes, md_name = _bytes_filenamepair_from_md(md)
    st.download_button(
        "⬇️ Download as Markdown (.md)",
        data=md_bytes,
        file_name=md_name,
        mime="text/markdown",
        use_container_width=True,
    )

    pdf_bytes, pdf_name = _fake_pdf_from_md(md)
    st.download_button(
        "⬇️ Download as PDF (demo)",
        data=pdf_bytes,
        file_name=pdf_name,
        mime="application/pdf",
        use_container_width=True,
        help="Demo-friendly PDF. Proper layout export will come in Phase 4.",
    )

    st.divider()
    st.subheader("Share (mock)")

    share_via = st.radio(
        "Channel",
        options=["Email", "Slack"],
        horizontal=True,
    )
    to_field = st.text_input("Recipient", placeholder="name@company.com or #channel")
    add_note = st.text_area("Note (optional)", placeholder="Anything to add?")

    if st.button("🚀 Share Brief (mock)", type="primary", use_container_width=True):
        # We log a history item for the share action so it appears in Insights
        history_item = {
            "type": "brief_share",
            "payload": {
                "channel": share_via.lower(),
                "to": to_field,
                "note": add_note,
                "file": "campaign_brief.md",
                "created_at": _now_iso(),
            },
            "result": "Mock share completed.",
            "tags": ["brief", "share", share_via.lower()],
        }
        st.session_state.setdefault("history", []).append(history_item)
        st.success(f"Shared via {share_via} (mock) to **{to_field or 'recipient'}**.")

st.divider()
with st.expander("Debug (what went into this brief?)"):
    st.write("Latest items found:")
    st.json(
        {
            "strategy": _latest_by_type("strategy"),
            "variants": _latest_by_type("variants"),
            "optimizer": _latest_by_type("optimizer") or _latest_by_type("word_optimizer"),
            "company": _get_company(),
        },
        expanded=False,
    )
