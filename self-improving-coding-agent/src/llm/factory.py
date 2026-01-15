from __future__ import annotations

import os
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class LLMNotConfiguredError(ValueError):
    pass


_llm = None


def get_llm() -> Optional[object]:
    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    if os.getenv("OPENROUTER_API_KEY"):
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="xiaomi/mimo-v2-flash:free",
            temperature=0,
        )
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4-turbo", temperature=0)
    return None


def ensure_llm() -> object:
    global _llm
    if _llm is None:
        _llm = get_llm()
        if _llm is None:
            raise LLMNotConfiguredError(
                "No API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY."
            )
    return _llm

