# shared/llm.py
from __future__ import annotations

import os
from typing import Optional

import streamlit as st

try:
    from openai import OpenAI
    from openai import AuthenticationError, APIConnectionError, BadRequestError, OpenAIError
except Exception:  # openai not installed or import error
    OpenAI = None
    AuthenticationError = APIConnectionError = BadRequestError = OpenAIError = Exception  # type: ignore


def _get_api_key() -> str:
    """Return OpenAI key from Streamlit secrets or env, trimmed."""
    key = (st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
    return key


def is_openai_ready() -> bool:
    """Do we have a non-empty key and the SDK available?"""
    return bool(OpenAI and _get_api_key())


def llm_copy(
    prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.6,
    max_tokens: int = 700,
) -> str:
    """
    Call OpenAI chat completions safely.
    Raises RuntimeError with short codes for callers to handle:
      - 'OPENAI_MISSING_KEY'
      - 'OPENAI_INVALID_KEY'
      - 'OPENAI_REQUEST_ERROR'
    """
    if not OpenAI:
        raise RuntimeError("OPENAI_REQUEST_ERROR")

    key = _get_api_key()
    if not key:
        raise RuntimeError("OPENAI_MISSING_KEY")

    try:
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise, brand-safe PR & marketing copywriter."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()
    except AuthenticationError:
        # Incorrect or expired key — don’t leak the key string
        raise RuntimeError("OPENAI_INVALID_KEY")
    except (BadRequestError, APIConnectionError, OpenAIError):
        raise RuntimeError("OPENAI_REQUEST_ERROR")
