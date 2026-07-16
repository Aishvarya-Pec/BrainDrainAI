from utils.fireworks_helper import generate_text, stream_text

SOLVER_MODEL = "accounts/fireworks/models/deepseek-v4-pro"
_SYSTEM = "I am BrainDrainAI — your AI study assistant. Read the user's problem or doubt and provide a helpful solution."


def solve_problem(prompt: str) -> str:
    """Answer a user's study problem or doubt."""
    return generate_text(SOLVER_MODEL, f"{_SYSTEM}\n\nUser: {prompt}", max_tokens=3000)


def solve_problem_stream(prompt: str):
    """Stream solution tokens for responsiveness."""
    return stream_text(SOLVER_MODEL, f"{_SYSTEM}\n\nUser: {prompt}", max_tokens=3000)