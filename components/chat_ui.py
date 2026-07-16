import streamlit as st
from core.solver import solve_problem_stream
from core.notes_generator import generate_notes_stream
from core.quizzer import create_quiz_json
from components.pdf_handler import generate_pdf_from_text, handle_pdf_upload


def _init_session_state():
    defaults = {
        "pdf_text": "",
        "pdf_announced": False,
        "messages": [],
        "quiz": None,
        "quiz_index": 0,
        "quiz_score": 0,
        "quiz_answered": False,
        "quiz_selected_idx": -1,
        "quiz_difficulty": None,
        "quiz_total": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _handle_pdf_announcement():
    pdf_text = handle_pdf_upload(key="chat_pdf_uploader")
    if pdf_text:
        st.session_state.pdf_text = pdf_text
        if not st.session_state.pdf_announced:
            snippet = pdf_text[:800]
            with st.chat_message("user"):
                st.markdown(f"📄 PDF content (snippet):\n\n{snippet}")
            st.session_state.messages.append({"role": "user", "content": f"📄 PDF content (snippet):\n\n{snippet}"})
            st.session_state.pdf_announced = True


def _process_mode(prompt: str, container):
    """Process a prompt through the selected mode and return response text."""
    selected_mode = st.session_state.get("mode_radio", "Solver")
    response_text = ""

    if selected_mode == "Solver":
        for chunk in solve_problem_stream(prompt):
            response_text += chunk
            container.markdown(response_text)

    elif selected_mode == "Notes Generator":
        for chunk in generate_notes_stream(prompt):
            response_text += chunk
            container.markdown(response_text)
        pdf_bytes = generate_pdf_from_text(response_text, title="BrainDrain Notes")
        st.download_button(
            label="📥 Download notes (PDF)",
            data=pdf_bytes,
            file_name="braindrain_notes.pdf",
            mime="application/pdf",
            help="Save your generated notes as a PDF",
        )

    elif selected_mode == "Quizzer":
        num_questions = st.session_state.get("quiz_num_questions", 10)
        data = create_quiz_json(prompt, "Medium", int(num_questions))
        st.session_state.quiz = data
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_answered = False
        st.session_state.quiz_selected_idx = -1
        st.session_state.quiz_difficulty = "Medium"
        st.session_state.quiz_total = len(data.get("quiz", []))
        response_text = "✅ Quiz generated. Scroll down to start answering."
        container.markdown(response_text)

    else:
        response_text = "⚠️ Unknown mode selected."
        container.markdown(response_text)

    return response_text


def _render_quiz_flow():
    """Render the interactive quiz UI."""
    quiz = st.session_state.quiz
    questions = quiz.get("quiz", [])
    if not questions:
        st.warning("No questions generated. Try another topic or reduce the question count.")
        return

    idx = st.session_state.quiz_index
    total = len(questions)

    st.progress(int((idx / max(total, 1)) * 100))
    st.caption(f"Score: {st.session_state.quiz_score} / {total}")

    if idx >= total:
        st.success(f"Final Score: {st.session_state.quiz_score} / {total}")
        if st.button("Restart quiz"):
            for key in ("quiz", "quiz_index", "quiz_score", "quiz_answered", "quiz_selected_idx", "quiz_difficulty", "quiz_total"):
                st.session_state[key] = None if key == "quiz" else (0 if key in ("quiz_index", "quiz_score", "quiz_total") else (False if key == "quiz_answered" else (-1 if key == "quiz_selected_idx" else None)))
        return

    q = questions[idx]
    st.markdown(f"**Question {idx + 1} of {total}**")
    st.markdown(q.get("question", ""))
    options = q.get("options", ["", "", "", ""])[:4]

    if not st.session_state.quiz_answered:
        choice = st.radio("Select an option:", options, key=f"quiz_choice_{idx}")
    else:
        selected_idx = st.session_state.quiz_selected_idx
        selected_val = options[selected_idx] if 0 <= selected_idx < len(options) else ""
        st.info(f"Your answer: {selected_val}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit answer", key=f"submit_{idx}") and not st.session_state.quiz_answered:
            correct_idx = int(q.get("answer_index", 0))
            try:
                selected_idx = options.index(st.session_state.get(f"quiz_choice_{idx}", options[0]))
            except ValueError:
                selected_idx = -1
            st.session_state.quiz_selected_idx = selected_idx
            if selected_idx == correct_idx:
                st.success("Correct ✅")
                st.session_state.quiz_score += 1
            else:
                st.error(f"Incorrect ❌. Correct: {options[correct_idx]}")
            explanation = q.get("explanation", "")
            if explanation:
                st.info(f"Explanation: {explanation}")
            st.session_state.quiz_answered = True
    with col2:
        if st.button("Next question", key=f"next_{idx}") and st.session_state.quiz_answered:
            st.session_state.quiz_index += 1
            st.session_state.quiz_answered = False
            st.session_state.quiz_selected_idx = -1


def chat_ui(selected_mode):
    """Main chat interface with history and mode-specific behavior."""
    _init_session_state()
    st.subheader(f"💬 BrainDrain Chat — Mode: {selected_mode}")

    _handle_pdf_announcement()

    # Quiz-specific controls
    if selected_mode == "Quizzer":
        st.session_state.quiz_num_questions = st.selectbox("Number of questions", [10, 20, 30, 50], index=0)

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Type your message (topic or passage for Quizzer)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("BrainDrain is thinking..."):
                container = st.empty()
                response_text = _process_mode(prompt, container)

        if selected_mode != "Quizzer":
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Quiz ready."})

    # Generate from PDF
    if st.session_state.pdf_text and st.button("Generate from PDF"):
        source = st.session_state.pdf_text
        st.session_state.messages.append({"role": "user", "content": "Using uploaded PDF content"})
        with st.chat_message("user"):
            st.markdown("Using uploaded PDF content")
        with st.chat_message("assistant"):
            with st.spinner("BrainDrain is reading your PDF..."):
                container = st.empty()
                response_text = _process_mode(source, container)

        if selected_mode != "Quizzer":
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Quiz ready from PDF."})

    # Interactive quiz flow
    if selected_mode == "Quizzer" and st.session_state.quiz:
        _render_quiz_flow()