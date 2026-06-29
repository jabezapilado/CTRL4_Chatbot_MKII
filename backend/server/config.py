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