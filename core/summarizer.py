from utils.fireworks_helper import generate_response, stream_response

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
    return generate_response(prompt.strip())


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
    return stream_response(prompt.strip())
