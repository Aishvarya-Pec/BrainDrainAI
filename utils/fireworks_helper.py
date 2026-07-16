import os
from typing import Iterable

from dotenv import load_dotenv

load_dotenv()

from fireworks.client import Fireworks

PREFERRED_MODEL = os.getenv("FIREWORKS_PREFERRED_MODEL", "accounts/fireworks/models/deepseek-v4-pro")

SYSTEM_PROMPT = (
    "You are BrainDrainAI, an AI study assistant. "
    "Respond concisely, clearly, and never mention any other product names."
)

_client: Fireworks | None = None


def _get_api_key() -> str:
    """Return API key from env or Streamlit secrets."""
    key = os.getenv("FIREWORKS_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("FIREWORKS_API_KEY", "")
    except Exception:
        return ""


def _get_client() -> Fireworks:
    global _client
    if _client is not None:
        return _client
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("FIREWORKS_API_KEY not configured. Add it to your .env or Streamlit secrets.")
    _client = Fireworks(api_key=api_key)
    return _client


def _chat_completion(model: str, prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    resp = _get_client().chat.completions.create(
        model=model, messages=messages, temperature=temperature, max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


def _yield_text_from_chunk(chunk) -> str | None:
    """Extract text delta from a streaming chunk."""
    try:
        if hasattr(chunk, "choices") and chunk.choices:
            choice = chunk.choices[0]
            delta = getattr(choice, "delta", None)
            if isinstance(delta, dict):
                return delta.get("content")
            if delta is not None and hasattr(delta, "content"):
                return getattr(delta, "content", None)
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                return choice.message.content
        return None
    except Exception:
        return None


def generate_text(model: str, prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> str:
    """Generate a response using the specified model."""
    try:
        return _chat_completion(model, prompt, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        return f"❌ AI unavailable: {e}"


def stream_text(model: str, prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> Iterable[str]:
    """Stream a response using the specified model."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    try:
        for chunk in _get_client().chat.completions.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, stream=True,
        ):
            text = _yield_text_from_chunk(chunk)
            if text:
                yield text
    except Exception as e:
        yield f"❌ AI streaming unavailable: {e}"