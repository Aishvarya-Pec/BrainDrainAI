import os
import json
from typing import Iterable

# Load env vars from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Optional: read Streamlit secrets if available
try:
    import streamlit as st
except Exception:
    st = None

# Fireworks client init with lazy setup to avoid import-time failures
try:
    from fireworks.client import Fireworks
except Exception:
    Fireworks = None

PREFERRED_MODEL = os.getenv("FIREWORKS_PREFERRED_MODEL", "accounts/fireworks/models/deepseek-v3p1")

# Global system prompt for persona
SYSTEM_PROMPT = (
    "You are BrainDrainAI, an AI study assistant. "
    "Respond concisely, clearly, and never mention any other product names."
)

client = None


def _get_api_key() -> str | None:
    """Find API key from env, .env, or Streamlit secrets."""
    key = os.getenv("FIREWORKS_API_KEY")
    if not key and st is not None:
        try:
            key = st.secrets.get("FIREWORKS_API_KEY", None)
        except Exception:
            key = None
    return key


def _get_client():
    """Lazily initialize and return the Fireworks client. Raises with a clear message if unavailable."""
    global client
    if client is not None:
        return client
    if Fireworks is None:
        raise RuntimeError("Fireworks client library not installed. Please install 'fireworks-ai'.")
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "FIREWORKS_API_KEY not configured. Add it to your .env or Streamlit secrets."
        )
    client = Fireworks(api_key=api_key)
    return client


def _chat_completion(model: str, prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    c = _get_client()
    resp = c.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


def generate_response(prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> str:
    """Generate response using the default preferred model."""
    try:
        return _chat_completion(PREFERRED_MODEL, prompt, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        return f"❌ AI unavailable: {e}"


# Helper to normalize streaming chunks across SDK variants
def _yield_text_from_chunk(chunk) -> str | None:
    try:
        # Fireworks responses stream style
        if hasattr(chunk, "type") and chunk.type in {"response.output_text.delta", "response.delta"}:
            return getattr(chunk, "delta", None)
        # OpenAI ChatCompletionChunk style
        if hasattr(chunk, "choices") and chunk.choices:
            choice = chunk.choices[0]
            # Some SDKs provide .delta.content; others nest under .delta
            delta = getattr(choice, "delta", None)
            if isinstance(delta, dict):
                return delta.get("content")
            if delta is not None and hasattr(delta, "content"):
                return getattr(delta, "content", None)
            # Fallbacks
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                return choice.message.content
        return None
    except Exception:
        return None


def stream_response(prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> Iterable[str]:
    """Stream response using the default preferred model (v2-style streaming)."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    try:
        c = _get_client()
        # Use v2 streaming: create(..., stream=True) and iterate chunks
        for chunk in c.chat.completions.create(
            model=PREFERRED_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        ):
            text = _yield_text_from_chunk(chunk)
            if text:
                yield text
    except Exception as e:
        yield f"❌ AI streaming unavailable: {e}"


def generate_response_with_model(model: str, prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> str:
    try:
        return _chat_completion(model, prompt, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        return f"❌ AI unavailable: {e}"


def stream_response_with_model(model: str, prompt: str, temperature: float = 0.7, max_tokens: int | None = None) -> Iterable[str]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    try:
        c = _get_client()
        for chunk in c.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        ):
            text = _yield_text_from_chunk(chunk)
            if text:
                yield text
    except Exception as e:
        yield f"❌ AI streaming unavailable: {e}"
