from __future__ import annotations

import os
from typing import Any

import openai

DEFAULT_BASE_URL = "https://api.tokedy.ai/v1"
API_KEY_URL = "https://tokedy.ai/app/keys"


def _resolve(api_key: str | None, base_url: str | None) -> tuple[str, str]:
    api_key = api_key or os.environ.get("TOKEDY_API_KEY")
    if not api_key:
        raise openai.OpenAIError(
            "No Tokedy API key found. Pass api_key=... or set the TOKEDY_API_KEY "
            f"environment variable. Create a key at {API_KEY_URL}"
        )
    base_url = base_url or os.environ.get("TOKEDY_BASE_URL") or DEFAULT_BASE_URL
    return api_key, base_url


class Tokedy(openai.OpenAI):
    """Client for the Tokedy API. Same interface as `openai.OpenAI`."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None, **kwargs: Any
    ) -> None:
        api_key, base_url = _resolve(api_key, base_url)
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)


class AsyncTokedy(openai.AsyncOpenAI):
    """Async client for the Tokedy API. Same interface as `openai.AsyncOpenAI`."""

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None, **kwargs: Any
    ) -> None:
        api_key, base_url = _resolve(api_key, base_url)
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
