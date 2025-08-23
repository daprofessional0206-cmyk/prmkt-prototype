# pages/06_Word_Optimizer.py
from __future__ import annotations

import streamlit as st

from shared import state
from shared.llm import llm_copy
from shared.history import add_history


def _make_prompts(text: str, tone: str, lang: str) -> tuple[str, str]:
    """Return (suggestions_prompt, rewrite_prompt)."""
    suggestions_prompt = f"""
You are a precise direct-response copy editor.
Analyze the following copy and list 6–10 **specific** improvements as bullet points.
Prefer strong action verbs (e.g., 'do'→'achieve', 'get'→'unlock'), remove filler,
make outcomes concrete (numbers, %, timelines), and end with one clear CTA suggestion.
Write bullets only — no preamble. Keep language: {lang}. Audience tone: {tone}.

COPY:
{text.strip()}
    """.strip()

    rewrite_prompt = f"""
You are a senior conversion copywriter.
Rewrite the copy below in {lang} with a {tone} tone.
Keep the meaning and any facts, but:
- replace weak verbs with strong action verbs,
- remove vague words ('nice', 'great'),
- make outcomes concrete (numbers, %, timelines) when implied,
- tighten sentences,
- keep formatting and line breaks.

Output only the rewritten copy (no commentary).

COPY:
{text.strip()}
    """.strip()

    return suggestions_prompt, rewrite_prompt


def _render_results():
    """Show current outputs from session_state."""
    left, right = st.columns(2)

    with left:
        st.subheader("Suggestions")
        sug = st.session_state.get("wo_suggestions")
        if sug:
            st.markdown(sug)
        else:
            st.caption("No suggestions yet.")

        st.download_button(
            "Download suggestions (.txt)",
            data=(sug or "").encode("utf-8"),
            file_name="word_optimizer_suggestions.txt",
            mime="text/plain",
            disabled=not bool(sug),
            use_container_width=True,
        )

    with right:
        st.subheader("Rewritten Copy")
        rw = st.session_state.get("wo_rewrite")
        if rw:
            st.markdown(rw)
        else:
            st.caption("No rewritten copy yet.")

        st.download_button(
            "Download rewritten copy (.txt)",
            data=(rw or "").encode("utf-8"),
            file_name="word_optimizer_rewrite.txt",
            mime="text/plain",
            disabled=not bool(rw),
            use_container_width=True,
        )


# --- Page setup --------------------------------------------------------------

st.set_page_config(page_title="Word Optimizer", page_icon="🧠", layout="wide")
st.title("🧠 Word Optimizer")

state.init()
co = state.get_company()

# Inputs
text = st.text_area(
    "Paste copy to improve",
    value=st.session_state.get("wo_text", ""),
    height=160,
    placeholder="Paste any paragraph, ad, landing page block, etc.",
)

colA, colB = st.columns(2)
with colA:
    tone = st.selectbox(
        "Tone",
        ["Professional", "Friendly", "Bold", "Playful", "Luxury", "Direct", "Empathetic"],
        index=0,
    )
with colB:
    lang = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi"], index=0)

st.session_state["wo_text"] = text

# Actions
c1, c2, c3 = st.columns([1.2, 1.2, 1])
suggest_btn = c1.button("Suggest Better Words", type="secondary", use_container_width=True)
rewrite_btn = c2.button("Rewrite Now", type="primary", use_container_width=True)
clear_btn = c3.button("Clear Output", use_container_width=True)

if clear_btn:
    st.session_state.pop("wo_suggestions", None)
    st.session_state.pop("wo_rewrite", None)
    st.success("Cleared.")

# Guard
if (suggest_btn or rewrite_btn) and not text.strip():
    st.warning("Please paste some copy first.")
    suggest_btn = rewrite_btn = False  # cancel actions

# Prompts
if suggest_btn or rewrite_btn:
    sug_prompt, rw_prompt = _make_prompts(text, tone, lang)

# Handle Suggest
if suggest_btn:
    try:
        suggestions = llm_copy(sug_prompt)
        # Small sanity fallback
        if not suggestions.strip():
            suggestions = (
                "- Replace weak verbs with action verbs.\n"
                "- Avoid vague language; make outcomes concrete.\n"
                "- Add a clear CTA."
            )
        st.session_state["wo_suggestions"] = suggestions

        # History (positional args to match your helper signature)
        add_history(
            "word_optimizer",
            {"action": "suggest", "tone": tone, "language": lang, "input": text},
            {"suggestions": suggestions},
            tags=["word_optimizer", "suggest", tone, lang],
        )
        st.success("Suggestions generated.")
    except Exception as e:
        st.error(f"LLM error while generating suggestions: {e}")

# Handle Rewrite
if rewrite_btn:
    try:
        rewrite = llm_copy(rw_prompt)
        if not rewrite.strip():
            rewrite = text  # fallback: echo original
        st.session_state["wo_rewrite"] = rewrite

        add_history(
            "word_optimizer",
            {"action": "rewrite", "tone": tone, "language": lang, "input": text},
            {"rewrite": rewrite},
            tags=["word_optimizer", "rewrite", tone, lang],
        )
        st.success("Rewrite generated.")
    except Exception as e:
        st.error(f"LLM error while rewriting: {e}")

# Results area
st.markdown("### Results")
_render_results()
