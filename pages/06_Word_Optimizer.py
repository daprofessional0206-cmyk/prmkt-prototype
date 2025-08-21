# pages/06_Word_Optimizer.py
from __future__ import annotations

import io
import json
from typing import List, Dict

import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Safe imports from shared modules (optional). We fall back gracefully if missing
# ──────────────────────────────────────────────────────────────────────────────
def _safe_has_openai() -> bool:
    try:
        from shared.state import has_openai  # type: ignore
        return bool(has_openai())
    except Exception:
        return "OPENAI_API_KEY" in st.secrets and bool(st.secrets["OPENAI_API_KEY"])

def _safe_brand_rules() -> str:
    try:
        from shared.state import get_brand_rules  # type: ignore
        return get_brand_rules() or ""
    except Exception:
        return ""

def _safe_add_history(kind: str, payload: Dict, output: str, tags: List[str] | None = None) -> None:
    """Use shared.history.add_history if available, otherwise local session storage."""
    try:
        from shared.history import add_history  # type: ignore
        add_history(kind, payload, output, tags=tags or [])
        return
    except Exception:
        pass
    # simple session fallback
    item = {
        "ts": st.session_state.get("_now", None),
        "kind": kind,
        "input": payload,
        "output": output,
        "tags": tags or [],
    }
    st.session_state.setdefault("history", [])
    st.session_state["history"].insert(0, item)
    st.session_state["history"] = st.session_state["history"][:50]

def _safe_llm(prompt: str, temperature: float = 0.3, max_tokens: int = 900) -> str:
    """Try shared.llm; if unavailable or offline, return an offline heuristic suggestion."""
    try:
        from shared.llm import generate  # type: ignore
        return (generate(prompt, temperature=temperature, max_tokens=max_tokens) or "").strip()
    except Exception:
        pass
    # Offline heuristic fallback
    return (
        "Draft:\n"
        "• Replace weak verbs with action verbs (e.g., 'do' → 'achieve', 'get' → 'unlock').\n"
        "• Avoid vague words (e.g., 'nice', 'great'); use specific outcomes (e.g., 'cut onboarding by 40%').\n"
        "• Add a clear CTA (e.g., 'Book a demo').\n"
    )

# ──────────────────────────────────────────────────────────────────────────────
# Compat: rerun on old/new Streamlit
# ──────────────────────────────────────────────────────────────────────────────
def _rerun():
    """Use st.rerun() if available; otherwise fall back gracefully."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()  # pragma: no cover
    else:
        # As a last resort, set a no-op flag so UI updates in-place
        st.session_state["_force_refresh"] = True

# ──────────────────────────────────────────────────────────────────────────────
# Page chrome
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Presence — Word Optimizer", page_icon="🧠", layout="wide")
st.title("🧠 Word Optimizer")
st.caption("Grammarly++ for marketing: suggest stronger words, rewrite for clarity/conversion/SEO, and keep brand rules.")

# subtle css
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.0rem; padding-bottom: 2.0rem; }
      .stTextArea textarea { font-size: 0.95rem; line-height: 1.45; }
      .opt-card { border:1px solid #2a2f45; border-radius:8px; padding:1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar status
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Status")
    if _safe_has_openai():
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Offline mode (heuristic suggestions)")

    st.subheader("📏 Brand Rules")
    br_rules = st.text_area(
        "Brand do’s/don’ts or banned words (optional)",
        value=_safe_brand_rules(),
        height=120,
        key="opt_brand_rules",
    )
    st.caption("These rules are used to avoid banned words and reinforce preferred phrasing.")

# ──────────────────────────────────────────────────────────────────────────────
# Main controls
# ──────────────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1])
with left:
    st.subheader("Input")
    user_text = st.text_area(
        "Paste copy to optimize",
        value="Acme RoboHub helps teams do work faster. It is very good and nice to use. Get started today!",
        height=220,
        key="opt_input",
    )

with right:
    st.subheader("Optimizer Settings")
    mode = st.selectbox(
        "Rewrite Mode",
        options=["Clarity", "Conversion", "SEO", "Formal", "Friendly"],
        index=0,
        key="opt_mode",
    )
    audience = st.text_input("Audience (optional)", value="Decision-makers", key="opt_audience")
    tone = st.selectbox("Tone (optional)", ["Neutral", "Professional", "Friendly", "Bold"], index=1, key="opt_tone")
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0, key="opt_lang")

st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# Actions (Suggest and Rewrite)
# ──────────────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    btn_suggest = st.button("Suggest Better Words", type="secondary", use_container_width=True)
with c2:
    btn_rewrite = st.button("Rewrite Now", type="primary", use_container_width=True)
with c3:
    btn_clear = st.button("Clear Output", use_container_width=True)

if "opt_output" not in st.session_state:
    st.session_state["opt_output"] = ""
if "opt_suggestions" not in st.session_state:
    st.session_state["opt_suggestions"] = ""

if btn_clear:
    st.session_state["opt_output"] = ""
    st.session_state["opt_suggestions"] = ""
    _rerun()

# ──────────────────────────────────────────────────────────────────────────────
# Build prompts
# ──────────────────────────────────────────────────────────────────────────────
BASE_INSTRUCTIONS = (
    "You are a senior marketing editor. Suggest evidence-driven word and phrase improvements for higher clarity and persuasion. "
    "Keep brand safety. If brand rules are provided, avoid banned words and follow preferences. "
)

def prompt_suggestions(text: str) -> str:
    return f"""{BASE_INSTRUCTIONS}
TASK: List concrete improvements as bullet points with 'Replace X → Y (reason: …)' and 'Add CTA: …' where helpful.

Brand rules:
{br_rules or '(none provided)'}

Audience: {audience or '(unspecified)'}
Tone: {tone}
Language: {language}

TEXT:
{text}
"""

def prompt_rewrite(text: str, mode: str) -> str:
    return f"""{BASE_INSTRUCTIONS}
TASK: Rewrite the text in '{mode}' mode. Keep meaning, improve clarity and impact. Respect brand rules and language. 
Return ONLY the rewritten copy (no commentary).

Brand rules:
{br_rules or '(none provided)'}

Audience: {audience or '(unspecified)'}
Tone: {tone}
Language: {language}

TEXT:
{text}
"""

# ──────────────────────────────────────────────────────────────────────────────
# Run actions
# ──────────────────────────────────────────────────────────────────────────────
if btn_suggest:
    if not user_text.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analyzing wording…"):
            resp = _safe_llm(prompt_suggestions(user_text), temperature=0.2, max_tokens=700)
        st.session_state["opt_suggestions"] = resp
        _safe_add_history(
            kind="optimizer_suggestions",
            payload={
                "mode": "Suggestions",
                "audience": audience,
                "tone": tone,
                "language": language,
                "brand_rules": br_rules,
                "text": user_text,
            },
            output=resp,
            tags=["optimizer", "suggestions", language, tone],
        )

if btn_rewrite:
    if not user_text.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Rewriting…"):
            resp = _safe_llm(prompt_rewrite(user_text, mode), temperature=0.35, max_tokens=800)
        st.session_state["opt_output"] = resp
        _safe_add_history(
            kind="optimizer_rewrite",
            payload={
                "mode": mode,
                "audience": audience,
                "tone": tone,
                "language": language,
                "brand_rules": br_rules,
                "text": user_text,
            },
            output=resp,
            tags=["optimizer", "rewrite", mode.lower(), language, tone],
        )

# ──────────────────────────────────────────────────────────────────────────────
# Results display
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("### Results")

colA, colB = st.columns([1, 1])

with colA:
    st.markdown("**Suggestions**")
    if st.session_state["opt_suggestions"]:
        st.markdown(f"<div class='opt-card'>{st.session_state['opt_suggestions']}</div>", unsafe_allow_html=True)
        st.download_button(
            "Download suggestions (.txt)",
            data=st.session_state["opt_suggestions"].encode("utf-8"),
            file_name="word_suggestions.txt",
            mime="text/plain",
            key="dl_suggestions",
            use_container_width=True,
        )
    else:
        st.caption("No suggestions yet. Click **Suggest Better Words**.")

with colB:
    st.markdown("**Rewritten Copy**")
    if st.session_state["opt_output"]:
        st.markdown(f"<div class='opt-card'>{st.session_state['opt_output']}</div>", unsafe_allow_html=True)
        st.download_button(
            "Download rewritten copy (.txt)",
            data=st.session_state["opt_output"].encode("utf-8"),
            file_name="rewritten_copy.txt",
            mime="text/plain",
            key="dl_rewrite",
            use_container_width=True,
        )
    else:
        st.caption("No rewrite yet. Click **Rewrite Now**.")
