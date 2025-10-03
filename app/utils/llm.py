import os

from langchain_openai import ChatOpenAI


def get_openai_llm(model: str = "gpt-4o-mini", temperature: float = 0.2) -> ChatOpenAI:
    """
    Returns an OpenAI Chat model instance. Uses a dummy key if not provided.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)



