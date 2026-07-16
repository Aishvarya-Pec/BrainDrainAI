from utils.fireworks_helper import generate_text, stream_text


def summarize_text(text: str) -> str:
    """Summarize long notes or text."""
    prompt = f"""
You are a Study Assistant that creates concise summaries from academic notes.

If the text is less than 50 words, say: 
"This text is too short to summarize. Please provide a longer passage."

Otherwise, summarize it into clear, bullet-point sections:
- Key Definitions
- Important Points
- Summary

Text: {text}
"""
    return generate_text("accounts/fireworks/models/deepseek-v4-pro", prompt.strip())


def summarize_text_stream(text: str):
    """Stream summary tokens for responsiveness."""
    prompt = f"""
You are a Study Assistant that creates concise summaries from academic notes.

If the text is less than 50 words, say: 
"This text is too short to summarize. Please provide a longer passage."

Otherwise, summarize it into clear, bullet-point sections:
- Key Definitions
- Important Points
- Summary

Text: {text}
"""
    return stream_text("accounts/fireworks/models/deepseek-v4-pro", prompt.strip())