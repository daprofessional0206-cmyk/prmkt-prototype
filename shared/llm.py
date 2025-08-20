# shared/llm.py
from __future__ import annotations
import os
from typing import Optional, Any
import streamlit as st

# We use the official OpenAI SDK v1.x
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


def is_openai_ready() -> bool:
    """Do we have a key and an importable SDK?"""
    key = None
    try:
        key = st.secrets.get("openai_api_key", None)
    except Exception:
        key = None
    key = key or os.getenv("OPENAI_API_KEY")
    return bool(key) and (OpenAI is not None)


def _client() -> Optional[Any]:
    """Return an OpenAI client if ready, else None."""
    if not is_openai_ready():
        return None
    key = None
    try:
        key = st.secrets.get("openai_api_key", None)
    except Exception:
        key = None
    key = key or os.getenv("OPENAI_API_KEY")
    assert key, "Missing OPENAI key"
    return OpenAI(api_key=key)


def llm_copy(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Simple text generator used by Strategy Ideas / Content Engine.
    Raises if the API fails so pages can show a friendly message.
    """
    cli = _client()
    if cli is None:
        raise RuntimeError("OpenAI key not configured")

    try:
        resp = cli.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior PR & marketing copywriter."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        raise RuntimeError(f"LLM error: {e}")
