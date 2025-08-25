# pages/04_Optimizer_Tests.py
from __future__ import annotations
import re
import streamlit as st
from shared import state, llm, history

st.set_page_config(page_title="Optimizer Tests", page_icon="✨", layout="wide")
st.title("✨ Optimized Copy")

state.init()
co = state.get_company()

draft = st.text_area("Paste your draft", height=160, value="")
c1, c2 = st.columns(2)
with c1:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Playful"], index=0)
with c2:
    lang = st.selectbox("Language", ["English"], index=0)

def _score(text: str) -> dict:
    # light heuristic for a quick demo (ok offline)
    s = {}
    s["Clarity"] = 5 - min(4, text.count(",") // 5)
    s["Persuasiveness"] = 3 + int(bool(re.search(r"(proven|results|increase|save|boost|win)", text, re.I)))
    s["Tone fit"] = 4 if tone.lower() in ["professional","friendly","bold","playful"] else 3
    s["Readability"] = 5 - min(4, len(max(text.splitlines() or [''], key=len)) // 120)
    return s

if "opt_output" not in st.session_state:
    st.session_state["opt_output"] = {"rewrite":"", "scores":{}}

if st.button("Run Optimizer", use_container_width=True):
    if not draft.strip():
        st.warning("Please paste some text.")
    else:
        prompt = f"""Rewrite the text to be clearer and more persuasive.
Company: {co.get('name','')} (Industry: {co.get('industry','')}).
Tone: {tone}. Language: {lang}.

Text:
\"\"\"{draft.strip()}\"\"\"

Return only the improved version."""
        try:
            rewrite = llm.llm_copy(prompt)
        except Exception:
            # fallback small rewrite
            rewrite = draft.replace("very ", "").replace("really ", "")
        scores = _score(rewrite)
        st.session_state["opt_output"] = {"rewrite": rewrite, "scores": scores}
        history.add(
            tool="Optimizer Tests",
            payload={"input": draft, "tone": tone, "language": lang},
            output={"rewrite": rewrite, "scores": scores},
            tags=["optimizer", lang, tone],
            meta={"company": co.get("name","N/A")},
        )

data = st.session_state["opt_output"]
if data["rewrite"]:
    st.subheader("1. Clearer, More Persuasive Rewrite:")
    st.markdown(data["rewrite"])
    st.subheader("2. Feedback Ratings")
    for k, v in data["scores"].items():
        st.markdown(f"- **{k}**: {v}")
