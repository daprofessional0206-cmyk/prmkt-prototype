# pages/04_Optimizer_Tests.py
from __future__ import annotations
import time
import streamlit as st

try:
    from shared.llm import llm_copy, is_openai_ready  # type: ignore
except Exception:
    def is_openai_ready() -> bool: return False
    def llm_copy(prompt: str) -> str:
        return "A) Version in neutral tone.\n\nB) Version in bold tone.\n\nC) Version in friendly tone."

try:
    from shared.history import add as add_history  # type: ignore
except Exception:
    def add_history(kind: str, payload: dict, output: str, tags=None):
        tags = tags or []
        st.session_state.setdefault("history", [])
        st.session_state["history"].append(
            {"kind": kind, "payload": payload, "output": output, "tags": tags, "ts": time.time()}
        )

def throttle(key: str, seconds: float) -> bool:
    now = time.time()
    last = st.session_state.get(key, 0.0)
    remain = seconds - (now - last)
    if remain > 0:
        st.info(f"Please wait {int(remain)}s before generating again.")
        return True
    st.session_state[key] = now
    return False

st.set_page_config(page_title="Optimizer Tests", page_icon="🧪", layout="wide")
st.title("Optimizer Tests")
st.caption("Test different tones, lengths, or styles to optimize messaging.")

base = st.text_area("Base message (one or two lines)", height=100)
tone_a, tone_b = st.columns(2)
with tone_a:
    t1 = st.selectbox("Tone A", ["Neutral", "Bold", "Friendly", "Professional"], index=0)
with tone_b:
    t2 = st.selectbox("Tone B", ["Neutral", "Bold", "Friendly", "Professional"], index=1)

if throttle("optimizer_cooldown", 3):
    st.stop()

if st.button("Run A/B Test", type="primary"):
    if not is_openai_ready():
        st.warning("OpenAI key missing — showing template output.")
    prompt = (
        f"Rewrite the following short message in two tones for A/B testing.\n"
        f"Message: {base}\nTones: {t1} and {t2}.\n"
        f"Label the outputs clearly as A) and B)."
    )
    try:
        out = llm_copy(prompt)
    except Exception as e:
        out = f"(Fallback) Unable to reach LLM.\n\n{e}"

    st.success("Test generated!")
    st.markdown(out)
    add_history("ab_test", {"prompt": prompt, "tones": [t1, t2], "base": base}, out, tags=["A/B", t1, t2])
