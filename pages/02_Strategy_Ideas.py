# pages/02_Strategy_Ideas.py
from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any, Dict

import streamlit as st

# ── Best‑effort imports from your shared helpers (safe fallbacks below) ─────────
try:
    from shared import state as _state  # type: ignore
except Exception:
    _state = None

try:
    from shared import llm as _llm  # type: ignore
except Exception:
    _llm = None

try:
    from shared import history as _hist  # type: ignore
except Exception:
    _hist = None


# ── Safe shims so this page never crashes if a helper is missing ───────────────
def _get_company() -> Dict[str, str]:
    """Return a company dict (name, industry, size, goals) with sensible defaults."""
    if _state and hasattr(_state, "get_company"):
        try:
            co = _state.get_company()
            # co may be a dataclass or dict – normalize:
            if hasattr(co, "__dict__"):
                co = asdict(co)  # type: ignore[arg-type]
            return {
                "name": co.get("name", "Acme Innovations"),
                "industry": co.get("industry", "Technology"),
                "size": co.get("size", "Mid-market"),
                "goals": co.get("goals", "Increase qualified demand and brand trust."),
            }
        except Exception:
            pass
    # defaults
    return {
        "name": "Acme Innovations",
        "industry": "Technology",
        "size": "Mid-market",
        "goals": "Increase qualified demand and brand trust.",
    }


def _has_openai() -> bool:
    if _state and hasattr(_state, "has_openai"):
        try:
            return bool(_state.has_openai())
        except Exception:
            return False
    # If llm helper can tell us
    if _llm and hasattr(_llm, "is_ready"):
        try:
            return bool(_llm.is_ready())
        except Exception:
            return False
    return False


def _call_llm(system: str, user: str, temperature: float = 0.6, max_tokens: int = 600) -> str:
    """
    Try several common function names in shared.llm so we don't break if
    your llm.py uses a different name.
    """
    if not _llm:
        raise RuntimeError("LLM helper not available.")
    # Common wrappers we might find in your shared/llm.py
    for fn_name in ("chat", "run_chat", "generate", "complete", "call_llm"):
        fn = getattr(_llm, fn_name, None)
        if fn:
            try:
                # Some wrappers accept (system, user, ...) and some accept messages list
                return fn(system=system, prompt=user, temperature=temperature, max_tokens=max_tokens)  # type: ignore
            except TypeError:
                # Try messages style
                try:
                    return fn(
                        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )  # type: ignore
                except Exception as e:
                    last_err = e
            except Exception as e:
                last_err = e
    # If we got here, none worked:
    raise RuntimeError(f"LLM wrapper not found/failed in shared.llm. Last error: {last_err}")


def _history_add(kind: str, payload: Dict[str, Any], output: Any) -> None:
    # Prefer shared.history.add if available
    if _hist and hasattr(_hist, "add"):
        try:
            _hist.add(kind=kind, payload=payload, output=output)
            return
        except Exception:
            pass
    # Fallback to st.session_state
    lst = st.session_state.setdefault("history", [])
    lst.insert(0, {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": kind, "input": payload, "output": output})
    st.session_state["history"] = lst[:30]


# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("🧭 Strategy Ideas")

co = _get_company()

with st.form("strategy_form", clear_on_submit=False):
    st.caption("Generate a practical PR/Marketing initiative tailored to your profile.")

    custom_goals = st.text_area(
        "Business Goals (optional override)",
        value=co["goals"],
        height=80,
    )

    colA, colB = st.columns([1, 1])
    with colA:
        tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Authoritative"], index=0)
    with colB:
        length = st.selectbox("Length", ["Very Short", "Short", "Medium"], index=2)

    submitted = st.form_submit_button("✨ Generate Strategy Idea", use_container_width=True)

if submitted:
    # Throttle spam (2s)
    now = time.time()
    last = st.session_state.get("last_strategy_ts", 0.0)
    if now - last < 2:
        st.info("⏳ Please wait a moment and try again.")
        st.stop()
    st.session_state["last_strategy_ts"] = now

    SYSTEM = (
        "You are a senior PR & Marketing strategist. "
        "Return only the idea, no preface. Use 4–6 concise bullets with headline, rationale, "
        "primary channel, top 2 tactics, and success metrics."
    )

    USER = f"""
Company: {co['name']} ({co['industry']}, size: {co['size']}).
Goals: {custom_goals or co['goals']}.
Tone: {tone}. Length: {length}.

Write a practical initiative we could run this month, with measurable metrics.
""".strip()

    try:
        with st.spinner("Thinking..."):
            if _has_openai():
                idea = _call_llm(SYSTEM, USER, temperature=0.55, max_tokens=420)
            else:
                # Offline fallback (never hangs)
                idea = f"""**Campaign Idea: “{co['name']} in Motion”**
- **Rationale:** Build tangible momentum for {co['industry']} buyers with fast, helpful education.
- **Primary channel:** LinkedIn thought leadership + earned PR snippets.
- **Tactics:** Two customer micro-stories, founder AMA thread, 3 how‑to posts, one simple ROI calculator.
- **Measurement:** CTR to calculator, demo requests, press pickups, and 30‑day lead retention.
- **Notes:** Keep tone {tone.lower()} and concise for {co['size'].lower()} buyers.
"""

        st.success("Strategy idea ready.")
        st.markdown(idea)

        _history_add(
            kind="strategy",
            payload={
                "company": co,
                "tone": tone,
                "length": length,
                "goals_used": custom_goals or co["goals"],
            },
            output=idea,
        )

    except Exception as e:
        st.error(f"Could not generate right now: {e}")
