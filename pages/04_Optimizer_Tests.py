import streamlit as st
from shared import state
from shared.llm import llm_copy
from shared.history import add_history

st.set_page_config(page_title="Optimizer Tests", page_icon="🧪", layout="wide")
st.title("🧪 Optimizer Tests")
st.caption("Test and optimize your draft content for clarity, persuasiveness, and tone.")

state.init()
co = state.get_company()

draft = st.text_area("Paste your draft", height=180)

if st.button("Run Optimization"):
    if not draft.strip():
        st.warning("Please paste a draft first.")
    else:
        with st.spinner("Optimizing..."):
            # LLM prompt for rewrite
            prompt = f"""
You are a copy optimization assistant.
Analyze the following draft and give:
1. A clearer, more persuasive rewrite.
2. Feedback ratings (Clarity, Persuasiveness, Call-to-Action) from 1-5 with explanations.

Draft:
{draft}
"""
            response = llm_copy(prompt)

        st.subheader("✨ Optimized Copy")
        st.write(response)

        # Save to history
        add_history(
            tool="Optimizer Tests",
            input=draft,
            output=response,
            meta={"company": getattr(co, "name", "N/A")}
        )

