import streamlit as st


def hero_ui():
    """Render the landing hero that matches the logo color theme without CTAs."""
    st.markdown(
        """
        <style>
        /* Hero section styles aligned with existing dark theme */
        .bd-hero {
          position: relative;
          padding: 2.5rem 1.25rem 2rem 1.25rem;
          border-radius: 16px;
          background: radial-gradient(1200px circle at 10% -20%, rgba(14,165,233,0.25), transparent 45%),
                      radial-gradient(800px circle at 90% -10%, rgba(236,72,153,0.25), transparent 40%),
                      #0b1020;
          border: 1px solid #1e293b;
          box-shadow: 0 20px 60px rgba(99,102,241,0.15);
          margin-bottom: 16px;
        }
        .bd-hero h1 {
          margin: 0 0 0.5rem 0;
          font-size: 2.1rem;
          line-height: 1.15;
          background: linear-gradient(90deg, #0ea5e9, #ec4899);
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }
        .bd-hero p.bd-subtitle {
          color: #cbd5e1;
          margin: 0.25rem 0 0 0;
          font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="bd-hero">
          <h1>BrainDrainAI — AI Study Assistant</h1>
          <p class="bd-subtitle">Understand topics faster, generate clean notes, and quiz yourself — all in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )