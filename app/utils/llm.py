import os
from typing import Optional

from langchain_openai import ChatOpenAI


def get_openai_llm(model: str = "gpt-4o-mini", temperature: float = 0.2, api_key: Optional[str] = None) -> ChatOpenAI:
    """
    Returns an OpenAI Chat model instance. Uses a dummy key if not provided.
    The real key can be provided via env var OPENAI_API_KEY or passed directly.
    """
    key = api_key or os.getenv("OPENAI_API_KEY") or "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"
    # langchain_openai ChatOpenAI reads api key from env by default, but we can pass directly
    return ChatOpenAI(model=model, temperature=temperature, api_key=key)


