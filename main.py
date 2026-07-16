import streamlit as st
from components.sidebar import sidebar_ui
from components.chat_ui import chat_ui
from components.hero import hero_ui
from components.theme import inject_global_theme

st.set_page_config(
    page_title="BrainDrainAI - AI Study Assistant",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# Inject global theme (fonts, colors, controls)
inject_global_theme()

# Sidebar
selected_mode = sidebar_ui()

# Landing hero
hero_ui()

# Main chat interface
st.divider()
chat_ui(selected_mode)