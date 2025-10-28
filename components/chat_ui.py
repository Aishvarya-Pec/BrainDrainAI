import streamlit as st
from core.solver import solve_problem_stream
from core.notes_generator import generate_notes_stream
from core.quizzer import create_quiz_json
from components.pdf_handler import generate_pdf_from_text, handle_pdf_upload


def chat_ui(selected_mode):
    """Main chat interface with history and mode-specific behavior."""

    st.subheader(f"💬 BrainDrain Chat — Mode: {selected_mode}")

    # Optional PDF upload to feed chat and modes
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""
    if "pdf_announced" not in st.session_state:
        st.session_state.pdf_announced = False
    pdf_text = handle_pdf_upload(key="chat_pdf_uploader")
    if pdf_text:
        st.session_state.pdf_text = pdf_text
        if not st.session_state.pdf_announced:
            snippet = pdf_text[:800]
            with st.chat_message("user"):
                st.markdown(f"📄 PDF content (snippet):\n\n{snippet}")
            st.session_state.messages.append({"role": "user", "content": f"📄 PDF content (snippet):\n\n{snippet}"})
            st.session_state.pdf_announced = True

    # Long-notes only: remove length selector
    # Previously used st.session_state.notes_length; now we force 'long' always

    # Quiz-specific controls (difficulty fixed to Medium; selector removed)
    difficulty = "Medium"
    num_questions = None
    if selected_mode == "Quizzer":
        num_questions = st.selectbox("Number of questions", [10, 20, 30, 50], index=0)

    # Initialize session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Initialize quiz session state
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_answered = False
        st.session_state.quiz_selected_idx = -1
        st.session_state.quiz_difficulty = None
        st.session_state.quiz_total = 0

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"]) 

    # User input box
    if prompt := st.chat_input("Type your message (topic or passage for Quizzer)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response based on mode
        with st.chat_message("assistant"):
            with st.spinner("BrainDrain is thinking..."):
                container = st.empty()
                response_text = ""

                if selected_mode == "Solver":
                    stream = solve_problem_stream(prompt)
                    for chunk in stream:
                        response_text += chunk
                        container.markdown(response_text)
                elif selected_mode == "Notes Generator":
                    # Force long notes generation
                    stream = generate_notes_stream(prompt, "long")
                    for chunk in stream:
                        response_text += chunk
                        container.markdown(response_text)
                    # Notes download option (PDF)
                    pdf_bytes = generate_pdf_from_text(response_text, title="BrainDrain Notes")
                    st.download_button(
                        label="📥 Download notes (PDF)",
                        data=pdf_bytes,
                        file_name="braindrain_notes.pdf",
                        mime="application/pdf",
                        help="Save your generated notes as a PDF"
                    )
                elif selected_mode == "Quizzer":
                    # Build a structured quiz and store in session for interactive flow
                    data = create_quiz_json(prompt, (difficulty or "Medium"), int(num_questions or 10))
                    st.session_state.quiz = data
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_selected_idx = -1
                    st.session_state.quiz_difficulty = (difficulty or "Medium")
                    st.session_state.quiz_total = len(data.get("quiz", []))
                    response_text = "✅ Quiz generated. Scroll down to start answering."
                    container.markdown(response_text)
                else:
                    response_text = "⚠️ Unknown mode selected."
                    container.markdown(response_text)

        # For Quizzer we only show a status message; other modes append full assistant text
        if selected_mode != "Quizzer":
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Quiz ready."})

    # Generate directly from PDF without typing
    if st.session_state.pdf_text:
        if st.button("Generate from PDF"):
            source = st.session_state.pdf_text
            st.session_state.messages.append({"role": "user", "content": "Using uploaded PDF content"})
            with st.chat_message("user"):
                st.markdown("Using uploaded PDF content")
            with st.chat_message("assistant"):
                with st.spinner("BrainDrain is reading your PDF..."):
                    container = st.empty()
                    response_text = ""

                    if selected_mode == "Solver":
                        stream = solve_problem_stream(source)
                        for chunk in stream:
                            response_text += chunk
                            container.markdown(response_text)
                    elif selected_mode == "Notes Generator":
                        # Force long notes generation from PDF
                        stream = generate_notes_stream(source, "long")
                        for chunk in stream:
                            response_text += chunk
                            container.markdown(response_text)
                        pdf_bytes = generate_pdf_from_text(response_text, title="BrainDrain Notes")
                        st.download_button(
                            label="📥 Download notes (PDF)",
                            data=pdf_bytes,
                            file_name="braindrain_notes.pdf",
                            mime="application/pdf",
                        )
                    elif selected_mode == "Quizzer":
                        data = create_quiz_json(source, (difficulty or "Medium"), int(num_questions or 10))
                        st.session_state.quiz = data
                        st.session_state.quiz_index = 0
                        st.session_state.quiz_score = 0
                        st.session_state.quiz_answered = False
                        st.session_state.quiz_selected_idx = -1
                        st.session_state.quiz_difficulty = (difficulty or "Medium")
                        st.session_state.quiz_total = len(data.get("quiz", []))
                        response_text = "✅ Quiz generated from PDF. Scroll down to start."
                        container.markdown(response_text)
                    else:
                        response_text = "⚠️ Unknown mode selected."
                        container.markdown(response_text)

            if selected_mode != "Quizzer":
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Quiz ready from PDF."})

    # Interactive Quiz Flow
    if selected_mode == "Quizzer" and st.session_state.quiz:
        quiz = st.session_state.quiz
        questions = quiz.get("quiz", [])
        if not questions:
            st.warning("No questions generated. Try another topic or reduce the question count.")
            return

        idx = st.session_state.quiz_index
        total = len(questions)

        # Progress and difficulty badge
        st.progress(int((idx / max(total, 1)) * 100))
        st.caption(f"Score: {st.session_state.quiz_score} / {total}")

        if idx >= total:
            st.success(f"Final Score: {st.session_state.quiz_score} / {total}")
            if st.button("Restart quiz"):
                st.session_state.quiz = None
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_answered = False
                st.session_state.quiz_selected_idx = -1
                st.session_state.quiz_difficulty = None
                st.session_state.quiz_total = 0
            return

        q = questions[idx]
        st.markdown(f"**Question {idx + 1} of {total}**")
        st.markdown(q.get("question", ""))
        options = q.get("options", ["", "", "", ""])[:4]

        # Show radio only if not answered; otherwise show locked selection
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
                # Lock the question: prevent re-submission or changing answer
                st.session_state.quiz_answered = True
        with col2:
            if st.button("Next question", key=f"next_{idx}") and st.session_state.quiz_answered:
                st.session_state.quiz_index += 1
                st.session_state.quiz_answered = False
                st.session_state.quiz_selected_idx = -1
