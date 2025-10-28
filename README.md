# BrainDrainAI — AI Study Assistant

![Framework](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit)  ![Language](https://img.shields.io/badge/Language-Python-yellow?logo=python)  ![Status](https://img.shields.io/badge/Status-Ready%20to%20Deploy-brightgreen)

BrainDrainAI helps you study faster with three focused modes: Solver, Notes Generator, and Quizzer — all in a clean Streamlit UI.

## ✨ Key Features
- Chat UI with modes: `Solver`, `Notes Generator`, `Quizzer`
- Optional PDF upload for context-aware answers and notes
- Download generated notes as PDF
- Difficulty and question count controls for quizzes
- Clean sidebar with current mode and model display

## 🎯 Modes & Capabilities
- Solver
  - Answers study questions clearly with step-by-step reasoning.
  - Handles math, CS, and general academic topics.
  - Streams responses for responsiveness.
  - Model: High-reasoning, general-purpose completion via Fireworks.
- Notes Generator (long-form only)
  - Produces extremely detailed, sectioned study notes (6–10+ sections).
  - Includes definitions, intuition, formal view, worked examples, edge cases, and pitfalls.
  - Outputs clean Markdown; supports downloading as PDF.
  - Model: Large instruct model via Fireworks.
- Quizzer
  - Generates structured MCQs with 4 options and concise explanations.
  - Difficulty scaling: Easy, Medium, Hard, God Level.
  - Robust answer parsing avoids bias to a specific option.
  - Interactive practice flow in the UI.
  - Model: Efficient 8B class via Fireworks.

## 🧩 Tech Stack
- Streamlit, Python
- Fireworks API client (`fireworks-ai`)
- `python-dotenv`, `PyPDF2`, `reportlab`, `pdfplumber`

## 📁 Project Structure
```
AI_StudyBuddy/
├── assets/            # logo
├── components/        # UI: chat_ui, hero, pdf_handler, sidebar, theme
├── core/              # features: explainer, notes_generator, quizzer, solver, summarizer
├── utils/             # fireworks_helper (env + client + helpers)
├── main.py            # Streamlit entry
├── requirements.txt   # deps
├── Procfile           # start command for hosts
├── render.yaml        # optional: Render deploy
└── .env.example       # sample envs
```

## 🔑 Environment
- Required: `FIREWORKS_API_KEY`
- Optional: `FIREWORKS_BASE_URL` (default Fireworks endpoint), `NOTES_MAX_TOKENS_LONG` (default 6500), `STREAMLIT_SERVER_PORT` (local default 8505)

Create local `.env` by copying `.env.example` and filling your values.

## 🧪 Local Run
- Install: `pip install -r requirements.txt`
- Start: `streamlit run main.py --server.port 8505`
- Open: `http://localhost:8505/`

## 🚀 Deploy to Streamlit Community Cloud
1) Push this repo to GitHub.
2) Go to Streamlit Cloud and create a new app.
3) Select your repo/branch and set entry point to `main.py`.
4) In Settings → Secrets, add `FIREWORKS_API_KEY`.
5) (Optional) Add other envs if you use overrides.
6) Deploy — your app will be live in minutes.

## 📝 Notes
- Notes Generator is optimized for long-form exhaustive coverage.
- Quizzer uses improved parsing to correctly map answers and explanations.
- Persona and branding are standardized to BrainDrainAI across UI and prompts.