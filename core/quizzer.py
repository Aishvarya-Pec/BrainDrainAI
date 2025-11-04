from utils.fireworks_helper import generate_response, stream_response
from utils.fireworks_helper import generate_response_with_model, stream_response_with_model
import json
import re
import random
QUIZ_MODEL = "accounts/fireworks/models/qwen3-8b"

# --- Sanitizers -------------------------------------------------------------

def _coerce_answer_index(ans, options, explanation: str | None = None):
    letters = ["A", "B", "C", "D"]
    # Numeric index directly
    if isinstance(ans, int):
        # Treat provided ints as 0-based; clamp to [0,3]
        return max(0, min(3, ans))
    s = str(ans or "").strip()
    # If empty, try explanation text
    if not s and explanation:
        s = str(explanation)
    # Try number inside string (e.g., "2", "Option 3")
    m_num = re.search(r"(?:option|choice|answer)\s*[:\-]?\s*(\d)", s, re.IGNORECASE)
    if m_num:
        try:
            n = int(m_num.group(1))
            # Heuristic: model often returns 1-based in text — convert 1..4 -> 0..3
            if 1 <= n <= 4:
                return n - 1
            return max(0, min(3, n))
        except Exception:
            pass
    try:
        n = int(s)
        # Convert 1-based 1..4 to 0..3 when provided as plain string
        if 1 <= n <= 4:
            return n - 1
        return max(0, min(3, n))
    except ValueError:
        pass
    # Try letter (e.g., "B", "Option C", "Answer: A")
    m_let = re.search(r"(?:option|choice|answer)\s*[:\-]?\s*([ABCD])", s, re.IGNORECASE)
    if m_let:
        ch = m_let.group(1).upper()
        if ch in letters:
            return letters.index(ch)
    s_up = s.upper()
    if s_up in letters:
        return letters.index(s_up)
    # Match by option text similarity
    def _norm(t: str) -> str:
        t2 = re.sub(r"[^a-z0-9]+", " ", str(t).lower())
        return " ".join(t2.split())
    s_norm = _norm(s)
    for i, o in enumerate(options[:4]):
        on = _norm(o)
        if not on:
            continue
        if on == s_norm or on in s_norm or s_norm in on:
            return i
    # As last resort, prefer non-empty first correct-looking option if explanation mentions it
    if explanation:
        exp_norm = _norm(explanation)
        for i, o in enumerate(options[:4]):
            if _norm(o) and _norm(o) in exp_norm:
                return i
    # Fallback: default to first option (index 0) to avoid confusion
    return 0


def _sanitize_quiz_dict(data: dict) -> dict:
    items = (
        data.get("quiz")
        or data.get("questions")
        or data.get("items")
        or []
    )
    out = []
    for q in items:
        question = str(q.get("question", "")).strip()
        options = q.get("options") or q.get("choices") or []
        options = [str(o) for o in options][:4]
        while len(options) < 4:
            options.append("")
        explanation = str(q.get("explanation", q.get("rationale", "")))
        ans = q.get("answer_index", q.get("answer"))
        idx = _coerce_answer_index(ans, options, explanation)
        out.append({
            "question": question,
            "options": options,
            "answer_index": idx,
            "explanation": explanation,
        })
    return {"quiz": out}

# --- Text (unused by UI but kept for completeness) -------------------------

def generate_quiz(text: str) -> str:
    """Generate quiz questions or flashcards from a topic or passage as plain text."""
    prompt = f"""
 I am BrainDrainAI — your AI study assistant. Create a mixed-format quiz from the user's topic or passage.
 
 If the input is a topic name (e.g., "DBMS", "Machine Learning"), 
 create questions on that topic.
 If it's a text passage, generate questions from the given content.
 Each question should include 4 options (A-D) and the correct answer below.
 The types of questions can be:
 - Multiple Choice
 - True/False
 - Fill in the Blanks
 - Descriptive
 Content: {text}
 """
    return generate_response_with_model(QUIZ_MODEL, prompt.strip(), max_tokens=1200)

# --- Streaming --------------------------------------------------------------

def generate_quiz_stream(text: str):
    """Stream quiz generation tokens for responsiveness."""
    prompt = f"""
You are a Study Assistant that creates quizzes for learning.

If the input is a topic name (e.g., "DBMS", "Machine Learning"), 
create questions on that topic.
If it's a text passage, generate questions from the given content.
Each question should include 4 options (A-D) and the correct answer below.
The types of questions can be:
- Multiple Choice
- True/False
- Fill in the Blanks
- Descriptive
Content: {text}
"""
    return stream_response_with_model(QUIZ_MODEL, prompt.strip(), max_tokens=1000)

# --- JSON quiz for UI -------------------------------------------------------

def _difficulty_examples(difficulty: str) -> str:
    examples = {
        "easy": (
            "Easy: Recall/recognition questions. Single-concept definitions and direct facts. "
            "Short stems, no multi-step reasoning. Distractors clearly incorrect; avoid tricks."
        ),
        "medium": (
            "Medium: Application/comprehension. Small scenarios with one-step reasoning or calculation. "
            "Plausible distractors reflecting common mistakes. Moderate stem length."
        ),
        "hard": (
            "Hard: Multi-step reasoning/calculation, integrate multiple concepts. Realistic scenarios or code snippets "
            "requiring analysis. Distractors include subtle misconceptions; careful reading required."
        ),
        "god level": (
            "God Level: Graduate/olympiad-style difficulty. Novel edge-case scenarios, multi-part reasoning, proof sketches or "
            "counterexamples. Numeric problems needing multiple computations; code with tricky edge cases. "
            "Distractors are very plausible but wrong for subtle reasons. Explanations briefly justify the correct choice "
            "and why others fail."
        ),
    }
    return examples.get(difficulty, "")


def create_quiz_json(topic_or_text: str, difficulty: str = "easy", num_questions: int = 10) -> dict:
    """Create a structured quiz as JSON for interactive use.

    Returns a dict with shape:
    {
      "quiz": [
        {"question": str, "options": [str, str, str, str], "answer_index": int, "explanation": str}
      ]
    }
    """
    difficulty = (difficulty or "easy").lower()
    if difficulty not in {"easy", "medium", "hard", "god level", "god"}:
        difficulty = "easy"
    if difficulty == "god":
        difficulty = "god level"
    num_questions = int(num_questions or 10)
    num_questions = num_questions if num_questions in {10, 20, 30, 50} else 10

    # Dynamic generation settings
    temp_map = {"easy": 0.2, "medium": 0.4, "hard": 0.6, "god level": 0.8}
    tok_map = {10: 1200, 20: 2000, 30: 2800, 50: 3800}
    temperature = temp_map.get(difficulty, 0.3)
    max_toks = tok_map.get(num_questions, 1200)

    schema = {
        "quiz": [
            {
                "question": "",
                "options": ["", "", "", ""],
                "answer_index": 0,
                "explanation": ""
            }
        ]
    }

    examples = _difficulty_examples(difficulty)

    prompt = f"""
 I am BrainDrainAI — your AI study assistant. Create a {difficulty} quiz with exactly {num_questions} questions from the user's topic or passage.
 
 Strict output rules:
 - OUTPUT MUST BE VALID JSON ONLY. NO extra text or markdown.
 - Use this exact schema: {schema}
 - "options" must have exactly 4 choices. Use clear, non-ambiguous options.
 - "answer_index" is the 0-based index of the correct option.
 - Include a concise "explanation" for the correct answer.
 
 Strict difficulty rules:
 {examples}
 - Match difficulty by required reasoning depth, not just wording.
 - Avoid repeating the same knowledge point across more than 20% of questions.
 - Question stems MUST be unique; do not rephrase the same question.
 - For "god level": at least 30% of questions require multi-step reasoning or formal justification.
 
 Diversity & coverage:
 - If input is a broad topic, distribute across important subtopics.
 - Mix skills: recall, understanding, application, synthesis (appropriately scaled by difficulty).
 
 Topic or Text Input:
 {topic_or_text}
 """

    # Get raw model output safely
    try:
        raw = generate_response_with_model(QUIZ_MODEL, prompt.strip(), temperature=temperature, max_tokens=max_toks)
    except Exception:
        return {"quiz": []}

    # Extract JSON if wrapped in code fences
    text_out = raw.strip()
    if "```" in text_out:
        start = text_out.find("```json")
        if start != -1:
            start += len("```json")
        else:
            start = text_out.find("```") + len("```")
        end = text_out.find("```", start)
        if end != -1:
            text_out = text_out[start:end].strip()

    # Parse JSON with robust fallback
    data = None
    try:
        data = json.loads(text_out)
    except Exception:
        try:
            start = text_out.find("{")
            end = text_out.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(text_out[start:end+1])
        except Exception:
            data = None

    if not isinstance(data, dict):
        data = {"quiz": []}

    data_sanitized = _sanitize_quiz_dict(data)
    if not data_sanitized.get("quiz"):
        # Fallback attempt with stricter prompt and alternative model
        strict_prompt = f"""
    Return ONLY valid JSON matching this exact schema (no markdown): {schema}
    Create a {difficulty} quiz with exactly {num_questions} questions.
    Topic or Text Input:
    {topic_or_text}
    """
        try:
            raw2 = generate_response_with_model("accounts/fireworks/models/deepseek-v3p1", strict_prompt.strip(), temperature=0.2, max_tokens=max_toks)
            try:
                parsed2 = json.loads(raw2)
            except Exception:
                s = raw2.find("{"); e = raw2.rfind("}")
                parsed2 = json.loads(raw2[s:e+1]) if s != -1 and e != -1 else {"quiz": []}
            data_sanitized = _sanitize_quiz_dict(parsed2)
        except Exception:
            # Last-resort synthetic quiz to avoid empty UI
            base = str(topic_or_text).strip() or "General Knowledge"
            gen = []
            for i in range(num_questions):
                stem = f"Which statement best describes {base}?"
                opts = [
                    f"A concise definition of {base}",
                    f"An unrelated concept",
                    f"A property of {base}",
                    f"An application of {base}"
                ]
                # Cycle correct index to avoid always 'A'
                gen.append({"question": stem, "options": opts, "answer_index": (i % 4), "explanation": f"The correct option matches the stem; others are distractors."})
            data_sanitized = {"quiz": gen}

    # Post-process: deduplicate, validate, and fill to exactly num_questions
    def _norm(s: str) -> str:
        return " ".join(str(s).lower().split())

    quiz = data_sanitized.get("quiz", [])
    seen = set()
    cleaned = []
    for q in quiz:
        stem = str(q.get("question", "")).strip()
        if not stem:
            continue
        key = _norm(stem)
        if key in seen:
            continue
        opts = [str(o).strip() for o in (q.get("options") or [])][:4]
        while len(opts) < 4:
            opts.append("")
        exp = str(q.get("explanation", q.get("rationale", "")).strip())
        ans = _coerce_answer_index(q.get("answer_index", q.get("answer")), opts, exp)
        cleaned.append({
            "question": stem,
            "options": opts,
            "answer_index": ans,
            "explanation": exp,
        })
        seen.add(key)

    def _synthesize(base: str, needed: int):
        templates = [
            "Which statement best describes {t}?",
            "Which is a core property of {t}?",
            "Which is a typical use-case for {t}?",
            "Which is NOT true about {t}?",
            "Which example best illustrates {t} in practice?",
            "Which benefit is associated with {t}?",
            "Which limitation often applies to {t}?",
            "Which step comes first when applying {t}?",
            "Which pitfall occurs when using {t} incorrectly?",
            "Which comparison correctly contrasts {t} with an alternative?",
        ]
        gen = []
        base_s = str(base).strip() or "General Knowledge"
        i = 0
        while len(gen) < needed:
            tmpl = templates[i % len(templates)]
            stem = tmpl.format(t=base_s) + f" [{i+1}]"
            options = [
                f"A concise definition of {base_s}",
                f"An unrelated concept to {base_s}",
                f"A property of {base_s}",
                f"An application of {base_s}",
            ]
            correct = (i % 4)
            exp = "The correct option matches the stem; others are distractors."
            gen.append({
                "question": stem,
                "options": options,
                "answer_index": correct,
                "explanation": exp,
            })
            i += 1
        return gen

    if len(cleaned) < num_questions:
        fill = _synthesize(topic_or_text, num_questions - len(cleaned))
        for q in fill:
            key = _norm(q["question"])
            if key in seen:
                continue
            cleaned.append(q)
            seen.add(key)

    # Randomize option order per question while preserving the correct index
    def _shuffle_question(q: dict) -> dict:
        opts = q.get("options", [])[:4]
        ans = int(q.get("answer_index", 0))
        # Pair original indices with options and shuffle
        pairs = list(enumerate(opts))
        random.shuffle(pairs)
        new_opts = [o for (_, o) in pairs]
        # Find new index of the originally correct option
        new_ans = next((i for i, (orig_idx, _) in enumerate(pairs) if orig_idx == ans), 0)
        return {
            "question": q.get("question", ""),
            "options": new_opts,
            "answer_index": new_ans,
            "explanation": q.get("explanation", ""),
        }

    final = cleaned[:num_questions]
    final = [_shuffle_question(q) for q in final]
    return {"quiz": final}
