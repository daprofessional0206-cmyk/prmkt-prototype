from __future__ import annotations

import json
import re
from dataclasses import asdict

import streamlit as st

from shared import state
from shared.llm import llm_copy  # uses your OpenAI key if present
from shared.history import add_history
from shared.types import CompanyProfile  # optional; used only for type hints

st.set_page_config(page_title="Optimizer Tests", page_icon="✨", layout="wide")

state.init()
co: CompanyProfile | dict = state.get_company()

st.title("✨ Optimizer Tests")

# ---------------- UI ----------------
left, right = st.columns([3, 1])
with left:
    source = st.text_area(
        "Paste copy to optimize",
        height=180,
        placeholder="Paste your paragraph, ad copy, email, or post here…",
    )
with right:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
    lang = st.selectbox("Language", ["English"], index=0)

c1, c2, c3 = st.columns([1, 1, 2])
rewrite = c1.button("Rewrite Now", type="primary")
suggest = c2.button("Suggest Better Words")
clear = c3.button("Clear Output")

if clear:
    st.session_state.pop("opt_result", None)

# -------------- Helpers --------------
def _company_hint(co_obj: CompanyProfile | dict) -> str:
    """Small context string for the model; safe for dict or dataclass."""
    if hasattr(co_obj, "name"):
        name = getattr(co_obj, "name", "")
        industry = getattr(co_obj, "industry", "")
        size = getattr(co_obj, "size", "")
    else:
        name = co_obj.get("name", "")
        industry = co_obj.get("industry", "")
        size = co_obj.get("size", "")
    return f"Company: {name} (Industry: {industry}, Size: {size})."

def _heuristic_scores(text: str) -> dict:
    """Fast local scoring if LLM not available."""
    words = text.split()
    clarity = 3 + (1 if len(words) < 160 else 0) + (1 if "." in text else 0)
    clarity = min(5, clarity)

    persuasive_tokens = ["you", "unlock", "save", "increase", "boost", "proven", "guarantee"]
    pers = 2 + sum(tok in text.lower() for tok in persuasive_tokens)
    pers = max(1, min(5, pers))

    specificity = 2
    if re.search(r"\d+%|\d+\.\d+|\b\d{4}\b", text):
        specificity += 2
    if any(k in text.lower() for k in ["in 7 days", "by q4", "within 2 weeks", "august"]):
        specificity += 1
    specificity = max(1, min(5, specificity))

    cta_strength = 2
    if re.search(r"\b(book a demo|get started|sign up|download|contact us|schedule)\b", text.lower()):
        cta_strength = 4
    if re.search(r"\bnow|today\b", text.lower()):
        cta_strength = min(5, cta_strength + 1)

    overall = round((clarity + pers + specificity + cta_strength) / 4, 1)
    return {
        "Clarity": clarity,
        "Persuasiveness": pers,
        "Specificity": specificity,
        "CTA Strength": cta_strength,
        "Overall": overall,
    }

def _llm_scores(original: str, improved: str) -> dict | None:
    """Ask the LLM to score; return dict or None on failure."""
    prompt = f"""
You are a copy editor. Compare ORIGINAL and IMPROVED and score 1–5:

Return strict JSON with keys: Clarity, Persuasiveness, Specificity, CTA Strength, Overall
and a brief 'Notes' string (<=40 words).

ORIGINAL:
{original}

IMPROVED:
{improved}
"""
    try:
        resp = llm_copy(prompt, max_tokens=200, json_mode=True)
        if isinstance(resp, dict):
            # normalize keys
            out = {}
            for k in ["Clarity", "Persuasiveness", "Specificity", "CTA Strength", "Overall", "Notes"]:
                if k in resp:
                    out[k] = resp[k]
            # sanity checks
            if all(k in out for k in ["Clarity", "Persuasiveness", "Specificity", "CTA Strength", "Overall"]):
                return out
        # sometimes models return a JSON string
        if isinstance(resp, str):
            j = json.loads(resp)
            return j
    except Exception:
        pass
    return None

def _rewrite_with_llm(text: str) -> str | None:
    system = (
        "Rewrite the text to be clearer, more specific, audience-oriented, and persuasive "
        "with a clear CTA. Keep brand-safe tone. Output plain paragraphs, no markdown."
    )
    try:
        return llm_copy(
            f"{system}\n\nTEXT:\n{text}",
            max_tokens=800,
        )
    except Exception:
        return None

def _suggestions_with_llm(text: str) -> str | None:
    try:
        return llm_copy(
            f"Suggest concrete improvements (bullets): verbs to replace, specifics to add, jargon to remove, and a strong CTA.\n\nTEXT:\n{text}",
            max_tokens=400,
        )
    except Exception:
        return None

# -------------- Actions --------------
result = st.session_state.get("opt_result")

if (rewrite or suggest) and not source.strip():
    st.warning("Paste some text first.")
elif rewrite or suggest:
    # Generate improved copy or suggestions
    improved = None
    suggestions = None

    if rewrite:
        improved = _rewrite_with_llm(source)
        if not improved:
            # Minimal local fallback
            improved = (
                "1. Clearer, More Persuasive Rewrite:\n\n"
                + re.sub(r"\s+", " ", source).strip()
                + "\n\n**CTA:** Book a demo to see how it fits your workflow."
            )

    if suggest:
        suggestions = _suggestions_with_llm(source)
        if not suggestions:
            suggestions = (
                "- Replace weak verbs with action verbs.\n"
                "- Add numbers/timeframes for specificity.\n"
                "- Reduce filler words; use shorter sentences.\n"
                "- Add a clear CTA (e.g., 'Book a demo today')."
            )

    # Scores (LLM first, fallback to heuristic)
    scores = _llm_scores(source, improved or source) if rewrite else None
    if not scores:
        scores = _heuristic_scores(improved or source)

    # Persist for render
    st.session_state["opt_result"] = {
        "improved": improved,
        "suggestions": suggestions,
        "scores": scores,
        "tone": tone,
        "lang": lang,
    }
    result = st.session_state["opt_result"]

    # ✅ Correct history write (positional arguments; no unsupported kwargs)
    # kind, payload, output, tags=None
    payload = {
        "tone": tone,
        "language": lang,
        "original": source,
        "company": asdict(co) if hasattr(co, "__dataclass_fields__") else co,
    }
    output = {
        "improved": improved,
        "suggestions": suggestions,
        "scores": scores,
    }
    try:
        add_history(
            "optimizer",
            payload,
            output,
            tags=["optimizer", tone, lang],
        )
    except Exception as e:
        st.info(f"(history note) Could not save this run: {e}")

# ---------------- Render ----------------
if not result:
    st.caption("Tip: Paste copy and click **Rewrite Now** or **Suggest Better Words**.")
else:
    improved = result.get("improved")
    suggestions = result.get("suggestions")
    scores = result.get("scores", {})

    st.header("Optimized Copy")
    if improved:
        st.markdown(improved)
    else:
        st.write("_No rewrite generated (try Suggest or Rewrite again)._")

    st.markdown("---")
    st.subheader("2. Feedback Ratings")

    # show each score
    for k in ["Clarity", "Persuasiveness", "Specificity", "CTA Strength"]:
        v = scores.get(k)
        if v is not None:
            st.write(f"- **{k}: {v}**")

    notes = scores.get("Notes")
    if notes:
        st.caption(f"Notes: {notes}")

    # suggestions block
    st.markdown("---")
    st.subheader("3. Suggestions")
    if suggestions:
        st.write(suggestions)
    else:
        st.write("_No suggestions generated in this run._")
