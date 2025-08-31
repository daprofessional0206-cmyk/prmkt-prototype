# shared/llm.py
from __future__ import annotations
from typing import Optional
import streamlit as st

SYSTEM_PROMPT = (
    "You are an expert PR & Marketing copywriter. "
    "Write clear, compelling, brand-safe copy. Follow brand rules if provided. "
    "Return copy only."
)

def _client():
    # Lazy import, no crash if missing
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return None, False
    try:
        from openai import OpenAI
        return OpenAI(api_key=key), True
    except Exception:
        return None, False

def llm_copy(user_prompt: str, model: str = "gpt-4o-mini",
             temperature: float = 0.6, max_tokens: int = 800) -> str:
    client, ok = _client()
    if not ok or client is None:
        # Offline fallback, simple template
        return (
            "Draft:\n"
            "• Opening line tailored to the audience.\n"
            "• Benefit/feature #1\n"
            "• Benefit/feature #2\n"
            "• Clear CTA"
        )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()
