import os
from typing import Optional

from dotenv import load_dotenv

from src.core.llm_provider import LLMProvider
from src.core.openai_provider import OpenAIProvider
from src.core.local_provider import LocalProvider


def create_llm_from_env(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """
    Build an LLMProvider from environment variables.
    DEFAULT_PROVIDER: openai | google | gemini | local
    """
    load_dotenv()
    p = (provider or os.getenv("DEFAULT_PROVIDER") or "openai").strip().lower()
    if p == "openai":
        m = model or os.getenv("DEFAULT_MODEL", "gpt-4o")
        key = os.getenv("OPENAI_API_KEY")
        return OpenAIProvider(model_name=m, api_key=key)
    if p in ("google", "gemini"):
        # Lazy import so local/openai-only runs do not load deprecated google.generativeai.
        from src.core.gemini_provider import GeminiProvider

        m = model or os.getenv("GEMINI_MODEL") or os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
        key = os.getenv("GEMINI_API_KEY")
        return GeminiProvider(model_name=m, api_key=key)
    if p == "local":
        path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=path)
    raise ValueError(f"Unknown provider '{p}'. Use openai, google/gemini, or local.")
