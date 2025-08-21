# pages/04_Optimizer_Tests.py
from __future__ import annotations

from typing import List, Dict, Any, Tuple
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Safe bridges into shared modules (fall back gracefully if missing)
# ──────────────────────────────────────────────────────────────────────────────
def _has_openai() -> bool:
    try:
        from shared.state import has_openai  # type: ignore
        return bool(has_openai())
    except Exception:
        return "OPENAI_API_KEY" in st.secrets and bool(st.secrets["OPENAI_API_KEY"])

def _get_company() -> Dict[str, str]:
    """Return a dict with company profile (never crash)."""
    try:
        from shared.state import get_company  # type: ignore
        co = get_company()
        # support dataclass or dict
        return dict(
            name=getattr(co, "name", None) or co.get("name", "Acme Innovations"),
            industry=getattr(co, "industry", None) or co.get("industry", "Technology"),
            size=getattr(co, "size", None) or co.get("size", "Mid-market"),
            goals=getattr(co, "goals", None) or co.get("goals", ""),
        )
    except Exception:
        return {"name": "Acme Innovations", "industry": "Technology", "size": "Mid-market", "goals": ""}

def _get_brand_rules() -> str:
    try:
        from shared.state import get_brand_rules  # type: ignore
        return get_brand_rules() or ""
    except Exception:
        return ""

def _add_history(kind: str, payload: Dict[str, Any], output: Any, tags: List[str] | None = None) -> None:
    """Use shared.history.add_history if present, otherwise session fallback."""
    try:
        from shared.history import add_history  # type: ignore
        add_history(kind, payload, output, tags=tags or [])
        return
    except Exception:
        pass
    item = {"kind": kind, "input": payload, "output": output, "tags": tags or []}
    st.session_state.setdefault("history", [])
    st.session_state["history"].insert(0, item)
    st.session_state["history"] = st.session_state["history"][:50]

def _llm(prompt: str, temperature: float = 0.6, max_tokens: int = 900) -> str:
    """Prefer shared.llm.generate; otherwise return offline template text."""
    try:
        from shared.llm import generate  # type: ignore
        return (generate(prompt, temperature=temperature, max_tokens=max_tokens) or "").strip()
    except Exception:
        pass
    # Offline fallback draft
    return (
        "Draft:\n"
        "• Opening line tailored to the audience.\n"
        "• Benefit/feature #1\n"
        "• Benefit/feature #2\n"
        "• Clear CTA\n"
    )

def _score_with_llm(text: str, criteria: List[str]) -> Tuple[Dict[str, int], int]:
    """Score text 1–10 per criterion and return (per_crit, total). LLM or heuristic."""
    prompt = f"""You are a strict marketing judge. Score the copy on each criterion from 1 (poor) to 10 (excellent).
Return as JSON with keys exactly: scores (per criterion), total.

Criteria: {', '.join(criteria)}

Copy:
{text}
"""
    try:
        from shared.llm import generate_json  # type: ignore
        res = generate_json(prompt, temperature=0.2, max_tokens=300)
        if isinstance(res, dict) and "scores" in res and "total" in res:
            # ensure ints
            scores = {k: int(v) for k, v in res["scores"].items()}
            total = int(res["total"])
            return scores, total
    except Exception:
        pass

    # heuristic fallback
    scores: Dict[str, int] = {}
    lower = text.lower()
    for c in criteria:
        if c.lower().startswith("clarity"):
            scores[c] = 7 + (1 if len(text) < 600 else 0)
        elif c.lower().startswith("persuasion"):
            bump = 1 if any(w in lower for w in ["save", "increase", "cut", "reduce", "grow", "book a demo"]) else 0
            scores[c] = 7 + bump
        elif c.lower().startswith("brand"):
            banned = any(w in lower for w in ["best-ever", "world's best", "guaranteed"])
            scores[c] = 8 - (2 if banned else 0)
        else:
            scores[c] = 7
    total = sum(scores.values())
    return scores, total

# ──────────────────────────────────────────────────────────────────────────────
# Page chrome
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Presence — Adaptive Copy Testing", page_icon="🧪", layout="wide")
st.title("🧪 Adaptive Copy Testing")
st.caption("Generate A/B/C variants, auto-score them for Clarity, Persuasion, and Brand-fit, and pick a winner.")

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.0rem; padding-bottom: 2rem; }
      .ab-card { border:1px solid #2a2f45; border-radius:8px; padding:1rem; }
      .winner { border:2px solid #24c48e !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar status
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Status")
    if _has_openai():
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Offline mode (heuristic drafts & scores)")

    st.subheader("📏 Brand Rules")
    st.caption("Used as constraints for generation and the brand-fit score.")
    brand_rules = st.text_area("Do’s / Don’ts (optional)", value=_get_brand_rules(), height=100)

# ──────────────────────────────────────────────────────────────────────────────
# Inputs
# ──────────────────────────────────────────────────────────────────────────────
co = _get_company()

left, right = st.columns([1, 1])

with left:
    content_type = st.selectbox(
        "Content Type",
        ["Ad", "Social Post", "Landing Page", "Email", "Press Release"],
        index=0,
        key="ab_content_type",
    )
    platform = st.selectbox(
        "Platform (if relevant)",
        ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"],
        index=0,
        key="ab_platform",
    )
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0", key="ab_topic")
    bullets = st.text_area("Key Points (one per line)", value="2× faster setup\nSOC 2 Type II\nSave 30% cost", height=120)

with right:
    audience = st.text_input("Audience", value="Decision-makers", key="ab_audience")
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold"], index=1, key="ab_tone")
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=0, key="ab_length")
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0, key="ab_lang")

st.markdown("---")

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    variants = st.slider("Variants (A/B/C)", min_value=1, max_value=3, value=2, step=1, key="ab_variants")
with c2:
    temperature = st.slider("Creativity", min_value=0.1, max_value=1.0, value=0.6, step=0.05, key="ab_temp")
with c3:
    crit = st.multiselect("Scoring criteria", ["Clarity", "Persuasion", "Brand-fit"], default=["Clarity", "Persuasion", "Brand-fit"], key="ab_criteria")

st.markdown("---")
run = st.button("Generate & Score", type="primary", use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# Build prompt for variants
# ──────────────────────────────────────────────────────────────────────────────
def _bulletize(text: str) -> List[str]:
    return [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()][:12]

def _prompt_for_variants(n: int) -> str:
    bullets_md = "\n".join([f"- {b}" for b in _bulletize(bullets)]) or "(no bullets provided)"
    return f"""
Generate {n} distinct variant(s) of a {length.lower()} {content_type.lower()} for platform "{platform}".
Language: {language}. Audience: {audience}. Tone: {tone}.
Company: {co['name']} (Industry: {co['industry']}, Size: {co['size']}).
Topic / Offer: {topic}

Key points:
{bullets_md}

Brand rules (follow; avoid banned words):
{brand_rules or "(none provided)"}

Constraints:
- Brand-safe, factual from provided info only.
- Strong opening, clear structure, crisp CTA.
- Make variants clearly different in angle, hook, or CTA.
Return ONLY the {n} variants, separated by a line with exactly: ---
"""

def _split_variants(text: str, n: int) -> List[str]:
    # split on the exact separator '---' on its own line
    parts = [p.strip() for p in text.split("\n---\n") if p.strip()]
    if len(parts) < n:
        # try a looser split
        parts = [p.strip() for p in text.split("---") if p.strip()]
    # pad if needed
    while len(parts) < n and parts:
        parts.append(parts[-1])
    return parts[:n] if parts else []

# ──────────────────────────────────────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Please enter a topic / offer first.")
    else:
        with st.spinner("Generating variants…"):
            raw = _llm(_prompt_for_variants(variants), temperature=temperature, max_tokens=1200)
            drafts = _split_variants(raw, variants) or [_llm(_prompt_for_variants(1), temperature=temperature)]

        results = []
        with st.spinner("Scoring variants…"):
            for d in drafts:
                scores, total = _score_with_llm(d, crit)
                results.append({"text": d, "scores": scores, "total": total})

        # pick winner
        winner_idx = max(range(len(results)), key=lambda i: results[i]["total"] if isinstance(results[i]["total"], int) else 0)

        st.success(f"Done. Winner: Variant {['A','B','C'][winner_idx]}")

        # display
        for i, res in enumerate(results):
            label = f"Variant {['A','B','C'][i]}"
            cls = "ab-card winner" if i == winner_idx else "ab-card"
            st.markdown(f"#### {label}")
            st.markdown(f"<div class='{cls}'>{res['text']}</div>", unsafe_allow_html=True)
            # scores table
            cols = st.columns(len(crit) + 1)
            for j, c in enumerate(crit):
                cols[j].metric(c, f"{res['scores'].get(c, 0)}/10")
            cols[-1].metric("Total", str(res["total"]))
            st.download_button(
                f"Download {label} (.txt)",
                data=res["text"].encode("utf-8"),
                file_name=f"ab_{['a','b','c'][i]}_{content_type.replace(' ','_').lower()}.txt",
                mime="text/plain",
                key=f"dl_{i}",
                use_container_width=True,
            )
            st.divider()

        # save to history
        _add_history(
            kind="ab_test",
            payload={
                "company": co,
                "content_type": content_type,
                "platform": platform,
                "topic": topic,
                "audience": audience,
                "tone": tone,
                "length": length,
                "language": language,
                "criteria": crit,
                "temperature": temperature,
            },
            output=results,
            tags=["ab_test", content_type, language, tone],
        )
