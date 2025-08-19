# shared/llm.py
from __future__ import annotations
import os
from typing import Optional

# Streamlit is optional here—used only to read st.secrets if available
try:
    import streamlit as st
except Exception:
    st = None  # type: ignore

# ---- Key loading ----
def _load_openai_key() -> Optional[str]:
    # 1) Streamlit Cloud / local .streamlit/secrets.toml
    if st and hasattr(st, "secrets"):
        key = st.secrets.get("OPENAI_API_KEY", None)  # type: ignore[attr-defined]
        if key:
            return str(key)

    # 2) Environment variable
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    return None

_OPENAI_KEY = _load_openai_key()

def is_openai_ready() -> bool:
    """Return True if an OpenAI API key is available."""
    return bool(_OPENAI_KEY)

# ---- Client factory ----
_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    if not is_openai_ready():
        raise RuntimeError("OpenAI key not set. Add it to .streamlit/secrets.toml or env var.")
    from openai import OpenAI
    _client = OpenAI(api_key=_OPENAI_KEY)
    return _client

SYSTEM_PROMPT = (
    "You are an expert PR & Marketing copywriter. "
    "Write clear, compelling, brand-safe copy using only provided facts. "
    "Match requested tone, audience, and length. Return only the copy."
)

def llm_copy(prompt: str, temperature: float = 0.6, max_tokens: int = 900) -> str:
    """
    Call OpenAI chat completion with a small, safe wrapper.
    Raises on API errors so the caller can fallback gracefully.
    """
    client = _get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()
