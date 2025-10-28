from utils.fireworks_helper import generate_response, stream_response
from utils.fireworks_helper import generate_response_with_model, stream_response_with_model
import os

NOTES_MODEL = "accounts/fireworks/models/mixtral-8x22b-instruct"

# Configurable token budgets
SHORT_MAX_TOKENS = int(os.getenv("NOTES_MAX_TOKENS_SHORT", "2200"))
LONG_MAX_TOKENS = int(os.getenv("NOTES_MAX_TOKENS_LONG", "6500"))


def generate_notes(text: str, length: str = "long") -> str:
    """Generate study notes from input text. Long-only (very detailed)."""
    # Force long mode regardless of input
    style = "long"
    temperature = 0.3

    prompt = f"""
I am BrainDrainAI — your AI study assistant. Create very detailed long study notes from the user's text.

Strict Coverage & Depth:
- Enumerate all core topics AND minor subtopics; do not skip small concepts.
- Group content into well-structured sections with clear hierarchy.
- Explain every concept thoroughly with definitions, intuition, and formal view.
- Include worked examples, edge cases, and step-by-step derivations or algorithms.
- Present formulas with variable definitions; for code, include annotated snippets.
- Call out common pitfalls and misconceptions; add practical tips.

Structure Requirements:
- Write AT LEAST 6–10 sections with `##` headings.
- Under each section, include 2–4 paragraphs (3–6 sentences each).
- Use occasional sub-bullets only when clarifying lists; do not switch to bullet-only output.
- Target overall length 1500–2500 words depending on topic scope.
- Continue until token budget is reached or coverage is exhaustive.

Output format:
- Markdown with headings (##) for sections; paragraphs under each.
- Use math/code blocks or inline formula notation when relevant.
- Maintain clarity: avoid rambling; keep explanations precise and rich.

Input Text:
{text}
"""
    return generate_response_with_model(
        NOTES_MODEL,
        prompt.strip(),
        temperature=temperature,
        max_tokens=LONG_MAX_TOKENS,
    )


def generate_notes_stream(text: str, length: str = "long"):
    """Stream study notes generation for responsiveness (long-only)."""
    style = "long"
    temperature = 0.3

    prompt = f"""
I am BrainDrainAI — your AI study assistant. Create very detailed long study notes from the user's text.

Strict Coverage & Depth:
- Enumerate all core topics AND minor subtopics; do not skip small concepts.
- Group content into well-structured sections with clear hierarchy.
- Explain every concept thoroughly with definitions, intuition, and formal view.
- Include worked examples, edge cases, and step-by-step derivations or algorithms.
- Present formulas with variable definitions; for code, include annotated snippets.
- Call out common pitfalls and misconceptions; add practical tips.

Structure Requirements:
- Write AT LEAST 6–10 sections with `##` headings.
- Under each section, include 2–4 paragraphs (3–6 sentences each).
- Use occasional sub-bullets only when clarifying lists; do not switch to bullet-only output.
- Target overall length 1500–2500 words depending on topic scope.
- Continue until token budget is reached or coverage is exhaustive.

Output format:
- Markdown with headings (##) for sections; paragraphs under each.
- Use math/code blocks or inline formula notation when relevant.
- Maintain clarity: avoid rambling; keep explanations precise and rich.

Input Text:
{text}
"""
    return stream_response_with_model(
        NOTES_MODEL,
        prompt.strip(),
        temperature=temperature,
        max_tokens=LONG_MAX_TOKENS,
    )