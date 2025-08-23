# shared/llm.py
from __future__ import annotations

import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # For type checkers only, import the OpenAI type
    from openai import OpenAI  # type: ignore
else:
    try:
        # OpenAI SDK v1 (runtime)
        from openai import OpenAI  # type: ignore
    except Exception:  # pragma: no cover
        OpenAI = None  # type: ignore

# --- API key helpers ---------------------------------------------------------

def _get_api_key() -> Optional[str]:
    """
    Reads key from Streamlit secrets (preferred) or environment.
    Works even if Streamlit isn't available.
    """
    # Try Streamlit secrets if available
    try:  # don't hard-depend on streamlit at import time
        import streamlit as st  # type: ignore
        if "openai_api_key" in st.secrets:
            key = str(st.secrets["openai_api_key"]).strip()
            if key:
                return key
    except Exception:
        pass

    # Fallback: environment variable
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key or None


def is_openai_ready() -> bool:
    """Backward-compatible readiness check used by some pages."""
    return bool(_get_api_key())


# --- Client factory ----------------------------------------------------------

def _client() -> "OpenAI":
    key = _get_api_key()
    if not key:
        raise RuntimeError(
            "OpenAI API key missing. Set Streamlit secret `openai_api_key` "
            "or env `OPENAI_API_KEY`."
        )
    if OpenAI is None:
        raise RuntimeError(
            "The `openai` package is not installed in this environment."
        )
    return OpenAI(api_key=key)


# --- Public LLM helpers ------------------------------------------------------

def llm_copy(
    prompt: str,
    *,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 800,
    system: str = "You are an expert marketing & PR writing assistant. Keep output clean Markdown.",
) -> str:
    """
    Minimal helper that returns a string completion for copy/ideas generation.
    Raises with a clear message if the SDK/key isn’t configured.
    """
    client = _client()

    # OpenAI SDK v1: chat.completions
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    text = (resp.choices[0].message.content or "").strip()
    return text
