"""
Language Service

Detects the language of a student's message.

Supported Languages
- English
- Filipino
- Taglish
- Unknown

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

import re
from dataclasses import dataclass


FILIPINO_WORDS = {
    "ako", "ikaw", "siya", "kami", "kayo", "sila",
    "po", "opo", "naman", "lang", "nga", "kasi",
    "hindi", "oo", "wala", "meron", "gusto",
    "salamat", "kumusta", "kamusta", "bakit",
    "pwede", "maaari", "natatakot", "nalulungkot",
    "galit", "masaya", "pagod", "problema",
    "aralin", "eskwela", "paaralan", "guidance"
}


ENGLISH_WORDS = {
    "i", "me", "my", "mine", "you", "your",
    "the", "and", "is", "are", "was", "were",
    "school", "student", "teacher", "professor",
    "subject", "exam", "assignment", "homework",
    "guidance", "appointment", "help", "please",
    "thank", "hello", "hi", "good", "bad"
}


@dataclass
class LanguagePrediction:

    language: str
    confidence: float


class LanguageService:

    def detect(self, text: str) -> LanguagePrediction:

        words = re.findall(r"\b[\w']+\b", text.lower())

        if not words:
            return LanguagePrediction(
                language="unknown",
                confidence=0.0
            )

        filipino_count = sum(
            word in FILIPINO_WORDS
            for word in words
        )

        english_count = sum(
            word in ENGLISH_WORDS
            for word in words
        )

        total = filipino_count + english_count

        if total == 0:

            return LanguagePrediction(
                language="unknown",
                confidence=0.0
            )

        filipino_ratio = filipino_count / total
        english_ratio = english_count / total

        if filipino_ratio >= 0.80:

            return LanguagePrediction(
                language="filipino",
                confidence=filipino_ratio
            )

        if english_ratio >= 0.80:

            return LanguagePrediction(
                language="english",
                confidence=english_ratio
            )

        return LanguagePrediction(
            language="taglish",
            confidence=max(
                filipino_ratio,
                english_ratio
            )
        )