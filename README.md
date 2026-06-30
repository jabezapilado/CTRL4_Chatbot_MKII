# Development of an AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

## Overview

- Web-based guidance chatbot for student support and inquiry handling.
- Flask backend serves chat, authentication, dashboard APIs, and MySQL persistence.
- Current AI stack is multilingual RAG (retrieval-augmented generation) with strict grounding to approved guidance content.
- Role-based routing is active: `student` to chatbot, `staff` and `admin` to dashboard.

## Current AI Architecture

- Active AI runtime: `backend/server/service.py` (`MultilingualRAGService`).
- Active knowledge source folder: `backend/knowledge_base/`.
- Active index build script: `backend/scripts/ingest_guidance_docs.py`.
- Chat endpoint: `POST /chat`.
- NLP-based negative emotion detection is active and can trigger immediate counselor escalation.
- Safety behavior includes crisis escalation and diagnosis refusal rules.

## Legacy AI Archive

The `ai/` folder is preserved as a **legacy archive** from the earlier prototype.

- It is **not** part of the current production runtime.
- Do not add new active chatbot logic there.
- Use it only for historical reference, comparison, or thesis documentation.

## Tech Stack

- Python 3.10+
- Flask, Flask-CORS
- MySQL / MariaDB (XAMPP)
- sentence-transformers, faiss-cpu, transformers (optional generator), langdetect
- pypdf and python-docx for document ingestion
- HTML, CSS, JavaScript frontend templates

## Quick Start

1. Start MySQL in XAMPP.
2. Configure backend environment values in `backend/.env`.
3. Setup backend environment and dependencies.
4. Build or refresh the RAG index.
5. Run Flask app.

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

## Key Endpoints

- `GET /health`
- `POST /chat`
- `POST /auth/login`
- `GET /api/inquiries`
- `GET /api/escalations`
- `GET /api/appointments`
- `GET /api/accounts`
- `GET /api/settings`

## Project Structure

```text
CTRL4_Chatbot/
├─ README.md
├─ frontend/
│  ├─ README.md
│  ├─ templates/
│  │  ├─ appointment.html
│  │  ├─ chatbot.html
│  │  ├─ chatbot_admin.html
│  │  ├─ dashboard.html
│  │  └─ login.html
│  └─ static/
│     ├─ css/
│     ├─ img/
│     └─ js/
├─ backend/
│  ├─ README.md
│  ├─ app.py
│  ├─ requirements.txt
│  ├─ setup.sh
│  ├─ .env.example
│  ├─ knowledge_base/
│  │  └─ hau_guidance_counseling_official.md
│  ├─ data/rag_index/
│  │  ├─ knowledge.faiss
│  │  └─ metadata.json
│  ├─ scripts/
│  │  ├─ ingest_guidance_docs.py
│  │  └─ setup_database.py
│  ├─ sql/
│  │  └─ schema.sql
│  └─ server/
│     ├─ __init__.py
│     ├─ auth.py
│     ├─ config.py
│     ├─ db.py
│     ├─ routes.py
│     └─ service.py
└─ ai/
   ├─ README.md (legacy archive note)
   ├─ chatbot_ai.py
   ├─ dataset.csv
   ├─ english_stopwords.txt
   ├─ goemotions_1.csv
   └─ tagalog_stopwords.txt
```

## Contributors

- Apilado, Jabez Timothy E. - Back-end Lead, Integration, and QA
- Quilantang, Grant Mihkael D. - Front-end Lead
- Lanix, Iligan - AI Model Lead
- Wylengco, Teyshaun Zell - UI/UX Lead

## License

This project is released for educational use. Apply additional licensing as needed before redistribution.