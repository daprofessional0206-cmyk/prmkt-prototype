# pages/06_Word_Optimizer.py
from __future__ import annotations

import streamlit as st
from shared import state, ui, llm, history

st.set_page_config(page_title="Word Optimizer", page_icon="🔤", layout="wide")
state.init()

ui.page_title("Word Optimizer", "Rewrite copy and suggest higher-performing wording.")

src = st.text_area("Your copy", height=200, placeholder="Paste text here…")
col1, col2, col3 = st.columns(3)
with col1:
    goal = st.selectbox("Goal", ["Click-throughs", "Sign-ups", "Purchases", "Engagement"], index=0)
with col2:
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Bold", "Conversational"], index=0)
with col3:
    lang = st.selectbox("Language", ["English", "Spanish", "French", "German", "Hindi", "Japanese"], index=0)

left, right = st.columns([1, 1])

with left:
    if st.button("🔁 Rewrite for Goal", use_container_width=True, disabled=not src.strip()):
        prompt = f"""
Rewrite the following copy in {lang} with a {tone.lower()} tone to maximize {goal.lower()}.
Keep meaning, improve clarity and persuasion. Output only the rewritten copy.

Text:
{src}
""".strip()
        try:
            if state.has_openai():
                out = llm.call(prompt, max_tokens=600, temperature=0.6)
            else:
                out = (
                    "Draft (offline):\n"
                    "• Opening line tailored to the audience.\n"
                    "• Benefit/feature #1\n"
                    "• Benefit/feature #2\n"
                    "• Clear CTA"
                )
            st.success("Rewritten.")
            st.markdown(out)
            history.add(
                kind="optimizer",
                text=out,
                payload={"prompt": prompt, "original": src, "goal": goal, "tone": tone, "language": lang},
                tags=["optimizer", goal, tone, lang],
                tool="Word Optimizer",
                meta={"company": state.get_company().name if hasattr(state.get_company(), "name") else ""},
            )
        except Exception as e:
            st.error(str(e))

with right:
    if st.button("💡 Suggest Better Words", use_container_width=True, disabled=not src.strip()):
        prompt = f"""
Suggest better words/phrases in {lang} for the copy below to improve {goal.lower()}.
Return a short bullet list: “Replace → With (why)”.

Copy:
{src}
""".strip()
        try:
            if state.has_openai():
                out = llm.call(prompt, max_tokens=500, temperature=0.4)
            else:
                out = (
                    "- “innovative solution” → “faster way to ___” (concrete benefit)\n"
                    "- “industry-leading” → “SOC2 Type II verified” (specific proof)"
                )
            st.success("Suggestions ready.")
            st.markdown(out)
            history.add(
                kind="optimizer",
                text=out,
                payload={"prompt": prompt, "original": src, "goal": goal, "tone": tone, "language": lang},
                tags=["optimizer", "suggestions", tone, lang],
                tool="Word Optimizer",
                meta={"company": state.get_company().name if hasattr(state.get_company(), "name") else ""},
            )
        except Exception as e:
            st.error(str(e))

st.divider()
if st.button("🧹 Clear input/output"):
    for k in list(st.session_state.keys()):
        if k.startswith("text") or k.startswith("textarea") or k.startswith("markdown"):
            st.session_state.pop(k, None)
    st.rerun()
