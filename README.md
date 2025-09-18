# 🧠 AI Task Manager (FastAPI + Gemini + LangGraph)

An AI-powered task management backend built using:

- 🧪 **FastAPI** – Lightweight REST and WebSocket backend
- 🧠 **Gemini API** via LangGraph – Natural language to action
- 🧰 **LangGraph** – Tool-based AI agent framework
- 🗂️ **PostgreSQL** – Task storage and filtering
- 🔌 **WebSockets** – Real-time chat interface

---

## 🌐 Live Chat API

Connect with the AI assistant via WebSocket:

ws://localhost:8000/ws/chat


---

## 🏗️ Features

- ✅ Create, update, delete tasks via natural language
- ✅ Parse due dates like “next Friday”
- ✅ Real-time AI chat interface (WebSocket)
- ✅ FastAPI + PostgreSQL REST endpoints
- ✅ Intent parsing & tool-calling via LangGraph
- ✅ Graceful error handling (e.g. invalid dates)

---

Getting Started

1️⃣ Clone the repo

```bash
git clone 
cd ai-task-manager

2️⃣ Set up a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3️⃣ Install dependencies
pip install -r requirements.txt
Do manual pip install for all other dependencies since import doesnot work even after adding it to requirements.txt

4️⃣ Set environment variables

Update the .env file:

GOOGLE_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://username:password@localhost/dbname

Or export manually:

export GOOGLE_API_KEY=your_gemini_api_key_here

5️⃣ Start PostgreSQL and run migrations

Use pgAdmin or psql CLI to create the database.

Running the Server
    uvicorn app.main:app --reload
