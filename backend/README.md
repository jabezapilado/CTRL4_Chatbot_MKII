# Backend

Project Title: Development of an AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

This folder contains the local Python backend for the chatbot.

Note: the instructions here are for local development. The final version will be deployed as a website and connected to a cloud database.

## Project Structure

```text
backend/
├─ README.md
├─ app.py
├─ requirements.txt
├─ setup.sh
├─ .env.example
├─ knowledge_base/
│  └─ hau_guidance_counseling_official.md
├─ data/rag_index/
│  ├─ knowledge.faiss
│  └─ metadata.json
├─ scripts/
│  ├─ ingest_guidance_docs.py
│  └─ setup_database.py
├─ sql/
│  └─ schema.sql
└─ server/
	├─ __init__.py
	├─ auth.py
	├─ config.py
	├─ db.py
	├─ routes.py
	└─ service.py
```

## What it provides

- Flask API for chat inference at `/chat`
- Role-based login at `/auth/login`
- MySQL/MariaDB persistence that works with XAMPP
- Admin/staff endpoints for inquiries, escalations, appointments, accounts, and settings
- Multilingual RAG chatbot service grounded to local approved documents
- NLP-based negative emotion detection for escalation to counselor support
- Safety guardrails for crisis escalation and diagnosis refusal

## Prototype Login

The first prototype can seed local accounts using environment variables in `backend/.env`.
Set `CHATBOT_SEED_*_PASSWORD` values before running setup if you want automatic seed accounts.

The login endpoint supports hashed credentials and also accepts legacy plaintext prototype values.

## Run locally

### First-time setup

1. Start MySQL in XAMPP.
2. Open a terminal in the [backend](.) folder.
3. Create the virtual environment and install the requirements.
4. Copy `.env.example` to `.env` and check your database settings.
5. Create the database and seed the default accounts.
6. Build the RAG index from the files in `knowledge_base/`.
7. Start the Flask app.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/setup_database.py
python scripts/ingest_guidance_docs.py
python app.py
```

### Daily run

If everything is already set up, use only:

```bash
cd backend
source .venv/bin/activate
python app.py
```

### Rebuild the RAG index after updating knowledge files

```bash
cd backend
source .venv/bin/activate
python scripts/ingest_guidance_docs.py
```

## Notes

- The backend now expects MySQL/MariaDB instead of SQLite.
- The database setup script creates the database, tables, and default student/staff/admin accounts.
- The bootstrap script installs dependencies, creates the virtual environment if needed, and seeds the database.
- The frontend is already wired to the backend endpoints in this workspace.
- The backend reads `.env` with `python-dotenv`, so run it from the project-local virtual environment.
- RAG behavior is configured through `CHATBOT_RAG_*` values in `.env`.
- Emotion escalation behavior is configured through `CHATBOT_EMOTION_ESCALATION_*` values in `.env`.
- Authentication now uses a Flask session cookie, so `CHATBOT_SECRET_KEY` must be set for production deployment.

## Legacy AI Archive

The top-level `../ai/` folder is retained only as historical prototype archive.

- It is not used by current backend runtime.
- Active chatbot behavior is defined in `server/service.py` and documents under `knowledge_base/`.