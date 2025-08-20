# shared/ui.py
from __future__ import annotations
import streamlit as st

def page_title(title: str, subtitle: str | None = None, icon: str | None = None) -> None:
    """
    Draw a consistent page title block at the top of each page.
    Usage: ui.page_title("Content Engine", "Generate brand-safe content", "📝")
    """
    # Top padding so titles aren't glued to the navbar
    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # Title line (with optional emoji icon)
    line = f"{icon} {title}" if icon else title
    st.markdown(f"<h1 style='margin-bottom:0.25rem'>{line}</h1>", unsafe_allow_html=True)

    # Subtitle (optional, small, muted)
    if subtitle:
        st.markdown(
            f"<div style='color:var(--text-color-secondary,#6b7280);"
            f"font-size:0.95rem;margin-bottom:0.75rem'>{subtitle}</div>",
            unsafe_allow_html=True,
        )

def hr(space: float = 0.5) -> None:
    """Thin divider with a bit of spacing."""
    st.markdown(
        f"<div style='margin:{space}rem 0;border-top:1px solid "
        "var(--border-color,#2a2a2a)'></div>",
        unsafe_allow_html=True,
    )

def badge(text: str) -> None:
    """Tiny pill badge for small hints."""
    st.markdown(
        f"<span style='display:inline-block;padding:2px 8px;border-radius:12px;"
        f"font-size:0.75rem;background:var(--secondary-background-color,#111827);"
        f"border:1px solid var(--border-color,#27272a);'>{text}</span>",
        unsafe_allow_html=True,
    )
