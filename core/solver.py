from utils.fireworks_helper import generate_response, stream_response
from utils.fireworks_helper import generate_response_with_model, stream_response_with_model
SOLVER_MODEL = "accounts/fireworks/models/deepseek-v3p1"


def solve_problem(prompt: str) -> str:
    """Answer a user's study problem or doubt."""
    system = (
        "I am BrainDrainAI — your AI study assistant. Read the user's problem or doubt and provide a helpful solution."
    )
    full_prompt = f"{system}\n\nUser: {prompt}"
    return generate_response_with_model(SOLVER_MODEL, full_prompt, max_tokens=3000)


def solve_problem_stream(prompt: str):
    """Stream solution tokens for responsiveness."""
    system = (
        "I am BrainDrainAI — your AI study assistant. Read the user's problem or doubt and provide a helpful solution."
    )
    full_prompt = f"{system}\n\nUser: {prompt}"
    return stream_response_with_model(SOLVER_MODEL, full_prompt, max_tokens=3000)