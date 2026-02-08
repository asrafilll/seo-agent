import os

from openai import AsyncOpenAI

from agents import set_default_openai_client


def configure_agent_client():
    """Configure the OpenAI Agents SDK client based on environment variables.

    Supports two providers:
    - openai (default): Uses standard OpenAI API
    - openrouter: Uses OpenRouter API for access to Qwen, Claude, etc.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        set_default_openai_client(client, use_for_tracing=False)
    else:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            client = AsyncOpenAI(api_key=api_key)
            set_default_openai_client(client, use_for_tracing=False)


def get_model_name():
    """Return the model name from env, with sensible defaults."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
