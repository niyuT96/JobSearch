"""LLM provider interfaces and helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.config import load_config


class LLMProvider(ABC):
    """Abstract provider for model calls."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a completion for a prompt.

        Args:
            prompt: Prompt text.

        Returns:
            str: Generated content.
        """

        raise NotImplementedError


class LangChainOpenAIProvider(LLMProvider):
    """LangChain-based provider using OpenAI-compatible chat models.

    This wrapper expects credentials to be provided via environment variables
    (e.g., OPENAI_API_KEY) and the model name via `model`.
    """

    def __init__(self, model: str, temperature: float = 0.0) -> None:
        load_config()
        self.model = model
        self.temperature = temperature
        self._client = _create_chat_model(model, temperature)

    def generate(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        return _extract_content(response)


def _create_chat_model(model: str, temperature: float):
    """Create a LangChain ChatOpenAI client.

    Args:
        model: Model name.
        temperature: Sampling temperature.

    Returns:
        Chat model instance with `.invoke()` support.
    """

    load_config()
    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature)
    except Exception:
        from langchain.chat_models import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature)


def _extract_content(response) -> str:
    """Extract text content from a LangChain response.

    Args:
        response: Response object or plain string.

    Returns:
        str: Content text.
    """

    if isinstance(response, str):
        return response
    content = getattr(response, "content", None)
    if content is not None:
        return str(content)
    return str(response)
