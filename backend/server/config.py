from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


class Config:
    def __init__(self) -> None:
        self.DB_HOST = os.getenv("CHATBOT_DB_HOST", "127.0.0.1")
        self.DB_PORT = int(os.getenv("CHATBOT_DB_PORT", "3306"))
        self.DB_USER = os.getenv("CHATBOT_DB_USER", "root")
        self.DB_PASSWORD = os.getenv("CHATBOT_DB_PASSWORD", "")
        self.DB_NAME = os.getenv("CHATBOT_DB_NAME", "soc_chatbot")
        self.DB_CHARSET = os.getenv("CHATBOT_DB_CHARSET", "utf8mb4")
        self.DB_SSL_CA = os.getenv("CHATBOT_DB_SSL_CA", "")
        self.DB_SSL_VERIFY_CERT = os.getenv("CHATBOT_DB_SSL_VERIFY_CERT", "false").lower() == "true"
        self.DEBUG = os.getenv("CHATBOT_DEBUG", "true").lower() == "true"
        self.SECRET_KEY = os.getenv("CHATBOT_SECRET_KEY", "dev-secret-key-change-me")
        self.PORT = int(os.getenv("CHATBOT_PORT", "5001"))

        self.SEED_STUDENT_EMAIL = os.getenv("CHATBOT_SEED_STUDENT_EMAIL", "student@hau.edu.ph")
        self.SEED_STUDENT_NAME = os.getenv("CHATBOT_SEED_STUDENT_NAME", "Maria Santos")
        self.SEED_STUDENT_PASSWORD = os.getenv("CHATBOT_SEED_STUDENT_PASSWORD", "")

        self.SEED_STAFF_EMAIL = os.getenv("CHATBOT_SEED_STAFF_EMAIL", "staff@hau.edu.ph")
        self.SEED_STAFF_NAME = os.getenv("CHATBOT_SEED_STAFF_NAME", "Ms. Reyes")
        self.SEED_STAFF_PASSWORD = os.getenv("CHATBOT_SEED_STAFF_PASSWORD", "")

        self.SEED_ADMIN_EMAIL = os.getenv("CHATBOT_SEED_ADMIN_EMAIL", "admin@hau.edu.ph")
        self.SEED_ADMIN_NAME = os.getenv("CHATBOT_SEED_ADMIN_NAME", "System Admin")
        self.SEED_ADMIN_PASSWORD = os.getenv("CHATBOT_SEED_ADMIN_PASSWORD", "")

        # Multilingual RAG configuration
        self.RAG_DOCS_DIR = os.getenv("CHATBOT_RAG_DOCS_DIR", str(BASE_DIR / "knowledge_base"))
        self.RAG_INDEX_DIR = os.getenv("CHATBOT_RAG_INDEX_DIR", str(BASE_DIR / "data" / "rag_index"))
        self.RAG_EMBEDDING_MODEL = os.getenv("CHATBOT_RAG_EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
        self.RAG_TOP_K = int(os.getenv("CHATBOT_RAG_TOP_K", "5"))
        self.RAG_MIN_SCORE = float(os.getenv("CHATBOT_RAG_MIN_SCORE", "0.30"))
        self.RAG_CHUNK_SIZE = int(os.getenv("CHATBOT_RAG_CHUNK_SIZE", "700"))
        self.RAG_CHUNK_OVERLAP = int(os.getenv("CHATBOT_RAG_CHUNK_OVERLAP", "120"))
        self.RAG_AUTO_BUILD_ON_START = os.getenv("CHATBOT_RAG_AUTO_BUILD_ON_START", "true").lower() == "true"
        self.RAG_GENERATOR_MODEL = os.getenv("CHATBOT_RAG_GENERATOR_MODEL", "")

        # Emotion-based escalation configuration
        self.EMOTION_ESCALATION_ENABLED = os.getenv("CHATBOT_EMOTION_ESCALATION_ENABLED", "true").lower() == "true"
        self.EMOTION_ESCALATION_THRESHOLD = float(os.getenv("CHATBOT_EMOTION_ESCALATION_THRESHOLD", "0.55"))