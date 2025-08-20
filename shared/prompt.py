from __future__ import annotations
from typing import Dict, Any
from .types import Company

def content_brief(content_type: str, company: Company, tone: str, length: str, lang: str) -> str:
    return (
        f"Content type: {content_type}\n"
        f"Company: {company.name or '—'} (Industry: {company.industry or '—'}, Size: {company.size or '—'})\n"
        f"Tone: {tone}; Length: {length}; Language: {lang}\n"
        f"Brand rules: {company.brand_rules or '—'}\n"
    )

def strategy_brief(goals: str, company: Company, tone: str, length: str) -> str:
    return (
        f"Goals: {goals or company.goals or '—'}\n"
        f"Company: {company.name or '—'} (Industry: {company.industry or '—'}, Size: {company.size or '—'})\n"
        f"Tone: {tone}; Length: {length}\n"
        f"Brand rules: {company.brand_rules or '—'}\n"
    )

# This file exists only to avoid import errors if you referenced "shared.prompt" earlier.
# The new pages don't require it, but it won't hurt to keep.
