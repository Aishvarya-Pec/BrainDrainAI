from utils.fireworks_helper import generate_response, stream_response

def explain_concept(concept: str) -> str:
    """Explain a concept in simple terms, detect irrelevant instructions."""
    prompt = f"""
You are a helpful Study Assistant. Your job is to explain academic concepts clearly.

If the user's input sounds like a topic (e.g., 'Normalization in DBMS' or 'Binary Trees'), 
explain it with key points, examples, and analogies.

If it sounds like an instruction (e.g., 'make a quiz', 'summarize this'), 
gently respond with: "It looks like you might want to use the Quizzer or Summarizer mode instead."

Topic: {concept}
"""
    return generate_response(prompt.strip())


def explain_concept_stream(concept: str):
    """Stream explanation tokens for responsiveness."""
    prompt = f"""
You are a helpful Study Assistant. Your job is to explain academic concepts clearly.

If the user's input sounds like a topic (e.g., 'Normalization in DBMS' or 'Binary Trees'), 
explain it with key points, examples, and analogies.

If it sounds like an instruction (e.g., 'make a quiz', 'summarize this'), 
gently respond with: "It looks like you might want to use the Quizzer or Summarizer mode instead."

Topic: {concept}
"""
    return stream_response(prompt.strip())
