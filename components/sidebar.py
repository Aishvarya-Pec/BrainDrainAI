import streamlit as st


def sidebar_ui():
    """Sidebar with compact branding, improved mode selector, and friendly model display."""

    # Initialize info panel state
    if "show_how_it_works" not in st.session_state:
        st.session_state.show_how_it_works = False

    # Sidebar-specific styling: compact top spacing, styled selectors
    st.markdown(
        """
        <style>
        /* Compact sidebar spacing */
        [data-testid="stSidebar"] .block-container { padding-top: 0rem; }

        /* Under-logo subtitle */
        .bd-side-subtitle { color: #94a3b8; margin: 0.25rem 0 0.75rem 0; font-size: 0.95rem; }

        /* Section headers: tighter bottom margin */
        .bd-section-title { color: #e5e7eb; font-weight: 600; margin: 0 0 0rem 0 !important; }

        /* Remove radio label gap and tighten radiogroup top spacing */
        .bd-radio { margin-top: 0 !important; }
        .bd-radio [data-testid="stRadio"] { margin: 0 !important; padding: 0 !important; }
        .bd-radio [data-testid="stRadio"] > label { display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }
        .bd-radio [role="radiogroup"] { margin: 0 !important; padding: 0 !important; }

        /* Radio group styling */
        .bd-radio [role="radiogroup"] > div {
          background: #0b1020; border: 1px solid #1e293b; border-radius: 12px; padding: 8px; margin-bottom: 6px;
        }
        .bd-radio label { color: #e2e8f0 !important; font-weight: 600; }

        /* Friendly model pill */
        .bd-model-pill {
          display: inline-block; padding: 6px 10px; border-radius: 999px;
          background: linear-gradient(90deg,#0ea5e9,#ec4899); color: white; font-weight: 600; font-size: 0.9rem;
        }

        /* Top bar buttons */
        .bd-topbar { margin: 0 0 0.4rem 0; }
        .bd-topbar .stButton > button { padding: 0.35rem 0.7rem; border-radius: 8px; font-weight: 600; background: linear-gradient(90deg,#0ea5e9,#ec4899); color: #fff; border: none; }
        .bd-topbar .stButton > button:hover { filter: brightness(1.08); }

        /* How it works panel */
        .bd-howworks { background: #0b1020; border: 1px solid #1e293b; border-radius: 12px; padding: 10px; margin-bottom: 8px; }
        .bd-howworks h4 { margin: 0 0 6px 0; font-size: 1rem; }
        .bd-howworks ul { margin: 0; padding-left: 1.1rem; }
        .bd-howworks li { margin: 4px 0; color: #e2e8f0; }
        .bd-howworks .bd-muted { color: #94a3b8; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Branding header with logo (compact) and a subtle subtitle
    st.sidebar.image("assets/logo.png", use_container_width=True)
    st.sidebar.markdown("<div class='bd-side-subtitle'>BrainDrainAI</div>", unsafe_allow_html=True)

    # Top bar buttons moved under the logo
    st.markdown("<div class='bd-topbar'>", unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button("🆕 New Chat", key="top_new_chat"):
            st.session_state.messages = []
            st.sidebar.success("Started a new chat!")
    with col2:
        if st.button("ℹ️ How it works", key="top_how_it_works"):
            st.session_state.show_how_it_works = not st.session_state.show_how_it_works
    st.markdown("</div>", unsafe_allow_html=True)

    # Optional: info panel explaining modes and models
    if st.session_state.show_how_it_works:
        st.sidebar.markdown(
            """
            <div class="bd-howworks">
              <h4>How it works</h4>
              <ul>
                <li><strong>Solver</strong> — DeepSeek V3.1: step-by-step solutions for math, code, and structured reasoning.</li>
                <li><strong>Notes Generator</strong> — Mixtral 8x22B Instruct: generates extremely detailed long-form study notes with rich sections.</li>
                <li><strong>Quizzer</strong> — Qwen3 8B: generates MCQs and tracks your score.</li>
              </ul>
              <p class="bd-muted">Components inside modes: Chat input, optional PDF upload (context), and controls like question count.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Close info", key="close_how_it_works"):
            st.session_state.show_how_it_works = False

    # Mode selection (improved UI)
    st.sidebar.markdown("<div class='bd-section-title'>🧩 Choose Mode</div>", unsafe_allow_html=True)
    with st.sidebar.container():
        # Apply our styled class around the radio
        st.markdown("<div class='bd-radio'>", unsafe_allow_html=True)
        mode = st.radio(
            "",
            ["Solver", "Notes Generator", "Quizzer"],
            index=0,
            label_visibility="collapsed",
            key="mode_radio",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Friendly model display by mode (no full ID)
    st.sidebar.markdown("<div class='bd-section-title'>🤖 Model</div>", unsafe_allow_html=True)
    MODELS_BY_MODE = {
        "Solver": ("DeepSeek V3.1", "accounts/fireworks/models/deepseek-v3p1"),
        "Notes Generator": ("Mixtral 8x22B Instruct", "accounts/fireworks/models/mixtral-8x22b-instruct"),
        "Quizzer": ("Qwen3 8B", "accounts/fireworks/models/qwen3-8b"),
    }
    model_name, model_id = MODELS_BY_MODE.get(mode, ("Unknown", ""))
    # Store the underlying id for potential future use
    st.session_state["selected_model_id"] = model_id
    st.sidebar.markdown(f"<span class='bd-model-pill'>{model_name}</span>", unsafe_allow_html=True)

    # Divider
    st.sidebar.markdown("---")

    # Footer note (minimal)
    st.sidebar.caption("© BrainDrainAI")
    return mode
