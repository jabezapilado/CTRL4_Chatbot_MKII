from __future__ import annotations

import re
import string
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


STOPWORDS = {"the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "po", "lang", "kasi"}
NEGATIVE_KEYWORDS = {
    "kill myself",
    "suicide",
    "hopeless",
    "worthless",
    "hurt myself",
    "hate everything",
    "anxious",
    "overwhelmed",
    "depressed",
    "angry",
    "furious",
    "frustrated",
}

INTENT_RULES = [
    {
        "patterns": [r"\boffice hours?\b", r"\bwhen is the office open\b", r"\bwhat time do you open\b"],
        "category": "office_hours",
        "response": "The SOC Guidance Office is open Monday to Friday, 8:00 AM to 5:00 PM.",
    },
    {
        "patterns": [r"\bbook an appointment\b", r"\bappointment\b", r"\bschedule a visit\b"],
        "category": "appointment",
        "response": "You can book an appointment through the appointment form and wait for confirmation from the Guidance Office.",
    },
    {
        "patterns": [r"\bcounseling\b", r"\bneed help\b", r"\btalk to a counselor\b"],
        "category": "counseling",
        "response": "You may request counseling support from the SOC Guidance Office. If this is urgent, please contact the office directly.",
    },
    {
        "patterns": [r"\brequirements?\b", r"\bprocedure\b", r"\bhow do i\b"],
        "category": "general_info",
        "response": "Please share the specific service you need so I can give the correct guidance office procedure.",
    },
]


def clean_and_preprocess(text: str) -> str:
    normalized = str(text).lower()
    normalized = re.sub(rf"[{re.escape(string.punctuation)}]", "", normalized)
    tokens = normalized.split()
    filtered = [word for word in tokens if word not in STOPWORDS]
    return " ".join(filtered)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _dataset_path() -> Path:
    return _project_root() / "ai" / "goemotions_1.csv"


def load_goemotions_dataset(file_path: Path) -> tuple[list[str], list[int]]:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing dataset: {file_path}")

    df = pd.read_csv(file_path)
    negative_emotion_columns = ["anger", "annoyance", "disappointment", "sadness"]

    if "example_very_unclear" in df.columns:
        df = df[df["example_very_unclear"] == False]

    df["target_label"] = df[negative_emotion_columns].max(axis=1)
    return df["text"].astype(str).tolist(), df["target_label"].astype(int).tolist()


@dataclass
class ChatResult:
    response: str
    emotion: str
    escalate: bool
    category: str
    confidence: float


class GuidanceChatbotService:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression(class_weight="balanced", max_iter=1000)
        self._trained = False

    def train(self) -> None:
        texts, labels = load_goemotions_dataset(_dataset_path())
        cleaned_texts = [clean_and_preprocess(text) for text in texts]
        features = self.vectorizer.fit_transform(cleaned_texts)
        self.model.fit(features, labels)
        self._trained = True

    def _predict_emotion(self, message: str) -> tuple[str, float]:
        if not self._trained:
            self.train()

        processed = clean_and_preprocess(message)
        features = self.vectorizer.transform([processed])
        probability = float(self.model.predict_proba(features)[0][1])
        emotion = "negative" if probability >= 0.55 else "neutral"
        return emotion, probability

    def _match_rule(self, message: str) -> tuple[str, str] | None:
        lowered = message.lower()
        for rule in INTENT_RULES:
            if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
                return rule["category"], rule["response"]
        return None

    def respond(self, message: str) -> ChatResult:
        emotion, confidence = self._predict_emotion(message)
        rule_match = self._match_rule(message)
        lower_message = message.lower()

        escalate = emotion == "negative" or any(keyword in lower_message for keyword in NEGATIVE_KEYWORDS)

        if escalate:
            response = (
                "I am sorry you are going through this. Your concern may need further attention from the Guidance Office, "
                "so it will be flagged for review."
            )
            category = "escalation"
        elif rule_match:
            category, response = rule_match
        else:
            category = "general"
            response = "I can help with office hours, appointments, counseling, and related guidance office inquiries."

        return ChatResult(
            response=response,
            emotion=emotion,
            escalate=escalate,
            category=category,
            confidence=confidence,
        )


@lru_cache(maxsize=1)
def get_chatbot_service() -> GuidanceChatbotService:
    service = GuidanceChatbotService()
    service.train()
    return service