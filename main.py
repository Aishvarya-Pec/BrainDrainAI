import streamlit as st
from components.sidebar import sidebar_ui
from components.chat_ui import chat_ui
from components.pdf_handler import handle_pdf_upload
from core.explainer import explain_concept
from core.summarizer import summarize_text
from core.quizzer import generate_quiz
from components.hero import hero_ui
from components.theme import inject_global_theme

st.set_page_config(
    page_title="BrainDrainAI - AI Study Assistant",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    },
)

# Global styling (refined spacing)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    p { line-height: 1.6; }
    h1, h2, h3 { letter-spacing: 0.2px; }

    /* Reduce top whitespace and move content upward */
    .stApp .block-container { padding-top: 0.5rem; }
    h1 { margin-top: 0.25rem; margin-bottom: 0.75rem; }

    /* Sidebar look (no forced open/close; allow native behavior) */
    [data-testid=\"stSidebar\"] { background-color: #0f172a; }
    [data-testid=\"stSidebar\"] * { color: #e2e8f0 !important; }
    [data-testid=\"stSidebar\"] .st-emotion-cache-1v0mbdj { background: #111827; border: 1px solid #1f2937; }

    /* Buttons and inputs */
    .stButton>button {
      border-radius: 10px;
      background: linear-gradient(90deg,#0ea5e9,#ec4899);
      color: white;
      border: 0;
      padding: 0.6rem 1rem;
      box-shadow: 0 8px 24px rgba(14,165,233,0.25);
    }
    .stRadio>div>label { font-weight: 600; }
    .stSelectbox div[data-baseweb=\"select\"] { border-radius: 10px; }

    /* Chat message styling */
    [data-testid=\"stChatMessage\"] {
      background: #0b1020;
      border: 1px solid #1e293b;
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 10px;
    }

    /* Quiz radio styling */
    .stRadio [role=\"radiogroup\"]>div { background: #0b1020; border: 1px solid #1e293b; border-radius: 12px; padding: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
selected_mode = sidebar_ui()

# Landing hero
hero_ui()

# Native Streamlit sidebar control: use the built-in arrow (no custom toggle)

# Inject global theme first
inject_global_theme()

# Main chat interface
st.divider()
chat_ui(selected_mode)

# Optional function preview
