# CTRL4 Chatbot MK II

> Development of an AI-Powered Guidance Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Gemini](https://img.shields.io/badge/Gemini-2.5--Flash-orange)
![Ollama](https://img.shields.io/badge/Ollama-Supported-green)
![RAG](https://img.shields.io/badge/RAG-Enabled-success)
![Version](https://img.shields.io/badge/Version-MK%20II%20Stable-success)

---

# Overview

CTRL4 Chatbot MK II is the second-generation AI-powered guidance chatbot developed for the **Holy Angel University – School of Computing**.

The system provides students with 24/7 guidance support by combining modern Artificial Intelligence technologies including Retrieval-Augmented Generation (RAG), multilingual Natural Language Processing (NLP), emotion-aware conversations, and official Guidance Office knowledge.

Unlike the first prototype (MK I), CTRL4 Chatbot MK II introduces a modular AI architecture that separates language understanding, emotion detection, safety validation, prompt engineering, knowledge retrieval, and LLM providers into independent services for improved scalability, maintainability, and future expansion.

---

# Project Status

**Current Version:** MK II Stable (v2.0.0)

CTRL4 Chatbot MK II is considered feature complete.

Major improvements over MK I include:

- Modular AI architecture
- Retrieval-Augmented Generation (RAG)
- Emotion-aware prompting
- Multilingual support
- Safety validation
- Provider abstraction
- Gemini integration
- Ollama integration
- Performance monitoring
- School of Computing branding
- Redesigned user interface

---

# Features

## Artificial Intelligence

- AI-powered Guidance Assistant
- Retrieval-Augmented Generation (RAG)
- Official Guidance Office Knowledge Base
- Emotion Detection
- Language Detection
- Emotion-aware Prompt Engineering
- Crisis Detection & Safety Validation
- Multilingual Support (English, Filipino, Taglish)
- Conversation Context Support

## LLM Providers

- Google Gemini API
- Ollama Local LLM
- Provider Abstraction Layer
- Easily Extendable Provider Architecture

## Student Features

- AI Chat Support
- Appointment Booking
- Guidance Office Information
- Conversation Export
- Responsive Interface

## Staff Features

- Admin Dashboard
- Student Concern Monitoring
- Chat Takeover Mode
- Appointment Management

---

# What's New in MK II

## Artificial Intelligence

Compared to MK I, CTRL4 Chatbot MK II introduces:

- Modular service-oriented AI architecture
- LLM Provider abstraction
- Retrieval-Augmented Generation (RAG)
- Emotion-aware prompting
- Crisis detection
- Performance monitoring
- Local AI support using Ollama
- Cloud AI support using Gemini

## User Interface

### MK I

- Holy Angel University branding
- Red theme
- Initial chatbot interface

### MK II

- School of Computing branding
- Orange theme
- Redesigned chatbot interface
- Improved user experience
- Cleaner layouts

---

# AI Architecture

```
                    Student
                        │
                        ▼
                 Frontend (HTML/CSS/JS)
                        │
                        ▼
                  Flask Backend API
                        │
                        ▼
                    AIService
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
 SafetyService   LanguageService   EmotionService
        │
        ▼
     RAGService
        │
        ▼
   PromptBuilder
        │
        ▼
     LLMService
        │
   ┌────┴────┐
   ▼         ▼
Gemini   Ollama
Provider Provider
```

---

# Technology Stack

## Backend

- Python 3.10+
- Flask
- Flask-CORS

## Artificial Intelligence

- Google Gemini API
- Ollama
- Sentence Transformers
- FAISS
- DistilBERT
- LangDetect

## Database

- MySQL / MariaDB

## Frontend

- HTML5
- CSS3
- JavaScript

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/CTRL4_Chatbot.git
cd CTRL4_Chatbot
```

---

## 2. Navigate to the Backend

```bash
cd backend
```

---

## 3. Create a Virtual Environment

```bash
python -m venv .venv
```

---

## 4. Activate the Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

---

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Configure Environment Variables

Create:

```text
backend/.env
```

Example:

```env
CHATBOT_LLM_PROVIDER=gemini

CHATBOT_GEMINI_API_KEY=YOUR_API_KEY
CHATBOT_GEMINI_MODEL=gemini-2.5-flash

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

---

## 7. Initialize the Database

Run the database setup script:

```bash
python scripts/setup_database.py
```

This command:

- Creates the application database.
- Creates the required database tables.
- Seeds the default user accounts.

### Default Development Accounts

| Role    |    Default Email     | Default Password |
|---------|----------------------|------------------|
| Student | `student@hau.edu.ph` |   `student123`   |
| Staff   | `staff@hau.edu.ph`   |   `staff123`     |
| Admin   | `admin@hau.edu.ph`   |   `admin123`     |

These credentials are intended for local development only. Update or replace them before deploying the application in any shared or production environment.

---

## 8. Build the Knowledge Base

```bash
python scripts/ingest_guidance_docs.py
```

This command generates the FAISS vector index used by the chatbot's Retrieval-Augmented Generation (RAG) pipeline.

---

## 9. Start the Application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

# Project Structure

```text
CTRL4_Chatbot/
│
├── ai_engine/                          # AI model development and training
│   ├── configs/
│   ├── core/
│   │   ├── models/
│   │   ├── preprocessors/
│   │   ├── schemas/
│   │   ├── tokenizers/
│   │   ├── training/
│   │   └── utilities/
│   │
│   ├── data/
│   │   ├── external/
│   │   ├── processed/
│   │   └── merged/
│   │
│   ├── knowledge_base/
│   └── models/
│
├── backend/                            # Flask backend and AI services
│   ├── data/
│   │   └── rag_index/
│   │
│   ├── scripts/
│   │   ├── ingest_guidance_docs.py
│   │   └── setup_database.py
│   │
│   ├── server/
│   │   ├── llm_providers/
│   │   │   ├── base_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   └── ollama_provider.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── emotion_service.py
│   │   │   ├── language_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── rag_service.py
│   │   │   └── safety_service.py
│   │   │
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── db.py
│   │   └── routes.py
│   │
│   ├── sql/
│   ├── app.py
│   ├── requirements.txt
│   └── setup.sh
│
├── frontend/                           # Web interface
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   │
│   └── templates/
│
├── docs/                               # Project documentation
│   ├── models/
│   │   ├── english_model/
│   │   └── filipino_model/
│   │
│   ├── 01_project_architecture.md
│   ├── 02_dataset_documentation.md
│   ├── 03_preprocessing_pipeline.md
│   ├── 04_model_architecture.md
│   ├── 05_api_integration.md
│   ├── 06_deployment_guide.md
│   ├── 07_future_work.md
│   ├── 08_design_decisions.md
│   └── CTRL4_BIBLE.md
│
├── CHANGELOG.md
├── LICENSE
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Screenshots

*(To be added before final release.)*

- Login Page
- Student Chat Interface
- Appointment Page
- Staff Dashboard
- Admin Chat Takeover
- AI Performance Logger

---

# Version History

## MK I

- Initial chatbot prototype
- Gemini-only implementation
- Holy Angel University branding
- Red theme
- Basic chatbot workflow

## MK II

- Complete AI architecture redesign
- Modular service-oriented architecture
- Retrieval-Augmented Generation (RAG)
- Emotion Detection
- Language Detection
- Safety Validation
- Prompt Engineering
- Gemini Provider
- Ollama Provider
- Performance Monitoring
- School of Computing branding
- Orange UI redesign
- Admin Dashboard
- Chat Takeover
- Conversation Export

---

# Future Work (MK III)

Planned enhancements include:

- Long-term conversation memory
- Counselor analytics dashboard
- Emotional trend visualization
- AI-generated counselor summaries
- Intent classification
- Streaming AI responses
- Real-time chat using WebSockets
- Migration to the Google Gen AI SDK

---

# Contributors

- **Apilado, Jabez Timothy E.**
  - Backend Development
  - Artificial Intelligence Integration
  - System Architecture
  - Database Development
  - Quality Assurance

- **Quilantang, Grant Mihkael D.**
  - Frontend Development

- **Lanix, Iligan**
  - AI Model Development

- **Wylengco, Teyshaun Zell**
  - UI/UX Design

---

# License

This project is licensed under the **CTRL4 Academic Use License**.

It is intended for academic, educational, and research purposes only. Commercial use, redistribution, or modification for commercial purposes requires permission from the authors.

See the [LICENSE](LICENSE) file for complete terms.