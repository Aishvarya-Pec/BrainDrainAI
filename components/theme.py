import streamlit as st


def inject_global_theme():
    """Inject app-wide CSS to match hero theme: fonts, colors, controls."""
    st.markdown(
        """
        <style>
        /* Import Inter font with fallbacks */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        :root {
          --bd-bg: #0b1020;
          --bd-text: #e2e8f0;
          --bd-muted: #94a3b8;
          --bd-border: #1e293b;
          --bd-accent-start: #0ea5e9;
          --bd-accent-end: #ec4899;
        }

        /* Base typography */
        .stApp, .stMarkdown, .stText, .stCaption, .st-emotion-cache-1v3fvfe {
          font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji' !important;
          color: var(--bd-text);
        }

        h1, h2, h3, h4, h5, h6 { color: var(--bd-text) !important; }
        p, li, label { color: var(--bd-text) !important; }
        small, .stCaption, .stMarkdown em { color: var(--bd-muted) !important; }
        a { color: var(--bd-accent-start) !important; }

        /* Buttons */
        .stButton > button {
          background: linear-gradient(90deg, var(--bd-accent-start), var(--bd-accent-end));
          color: #ffffff; border: none; border-radius: 10px; padding: 0.5rem 0.9rem; font-weight: 600;
        }
        .stButton > button:hover { filter: brightness(1.08); }

        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox > div > div,
        .stNumberInput input {
          color: var(--bd-text) !important; background: #0f172a !important; border: 1px solid var(--bd-border) !important; border-radius: 10px !important;
        }
        .stSelectbox [data-baseweb="select"] > div { color: var(--bd-text) !important; }

        /* File uploader */
        [data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"],
        [data-testid="stFileUploader"] section {
          color: var(--bd-text) !important;
        }
        [data-testid="stFileUploader"] .st-emotion-cache-1vbkxwb { background: #0f172a !important; border: 1px dashed var(--bd-border) !important; }

        /* Chat messages */
        [data-testid="stChatMessage"] { background: #0f172a; border: 1px solid var(--bd-border); border-radius: 12px; }
        [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { color: var(--bd-text) !important; }

        /* Sidebar */
        [data-testid="stSidebar"] .block-container { color: var(--bd-text); }
        [data-testid="stSidebar"] .stMarkdown { color: var(--bd-text) !important; }

        /* Headers / section titles consistency */
        .bd-section-title { color: var(--bd-text); }
        .bd-side-subtitle { color: var(--bd-muted); }

        /* Radio/select containers */
        .bd-radio [role="radiogroup"] > div { background: #0f172a; border: 1px solid var(--bd-border); }

        /* Model pill */
        .bd-model-pill { background: linear-gradient(90deg, var(--bd-accent-start), var(--bd-accent-end)); }
        </style>
        """,
        unsafe_allow_html=True,
    )