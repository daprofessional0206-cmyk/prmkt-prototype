# pages/02_Strategy_Ideas.py
from __future__ import annotations
import time
import streamlit as st

# --- soft imports -------------------------------------------------------------
try:
    from shared import state  # type: ignore
except Exception:
    class _State:
        def init(self): st.session_state.setdefault("company", {})
        def get_company(self): self.init(); return st.session_state["company"]
    state = _State()  # type: ignore

try:
    from shared.llm import llm_copy, is_openai_ready  # type: ignore
except Exception:
    def is_openai_ready() -> bool: return False
    def llm_copy(prompt: str) -> str:
        return "Draft:\n• Opening line tailored to audience.\n• Benefit/feature #1\n• Benefit/feature #2\n• Clear CTA"

try:
    from shared.history import add as add_history  # type: ignore
except Exception:
    def add_history(kind: str, payload: dict, output: str, tags=None):
        tags = tags or []
        st.session_state.setdefault("history", [])
        st.session_state["history"].append(
            {"kind": kind, "payload": payload, "output": output, "tags": tags, "ts": time.time()}
        )

# --- helpers ------------------------------------------------------------------
def throttle(key: str, seconds: float) -> bool:
    now = time.time()
    last = st.session_state.get(key, 0.0)
    remain = seconds - (now - last)
    if remain > 0:
        st.info(f"Please wait {int(remain)}s before generating again.")
        return True
    st.session_state[key] = now
    return False

# --- page ---------------------------------------------------------------------
st.set_page_config(page_title="Strategy Ideas", page_icon="💡", layout="wide")
state.init()
st.title("Strategy Ideas")
st.caption("Brainstorm bold PR & marketing angles quickly.")

co = state.get_company()
audiences = ["Decision-makers", "Developers", "Consumers", "Investors", "Journalists"]
tone = st.selectbox("Tone", ["Neutral", "Bold", "Funny", "Inspirational"], index=0)
aud = st.selectbox("Audience", audiences, index=0)
how_many = st.slider("How many ideas?", 3, 8, 5)

if throttle("strategy_cooldown", 4):
    st.stop()

if st.button("Generate Ideas", type="primary", use_container_width=True):
    if not is_openai_ready():
        st.warning("OpenAI key missing — showing template output.")
    prompt = (
        f"Generate {how_many} concise PR/marketing strategy ideas for a company.\n"
        f"Company: {co.get('name','(Company)')} in {co.get('industry','(Industry)')}, size {co.get('size','Mid-market')}.\n"
        f"Business goals: {co.get('goals','(Goals)')}.\n"
        f"Audience: {aud}. Tone: {tone}.\n"
        "Return a numbered list."
    )
    try:
        text = llm_copy(prompt)
    except Exception as e:
        text = f"(Fallback) Unable to reach LLM.\n\n{e}"

    st.success("Ideas generated!")
    st.markdown(text)
    add_history("strategy", {"prompt": prompt}, text, tags=["Strategy", tone, aud])
