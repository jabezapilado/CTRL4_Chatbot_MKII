"""
Safety Service

Performs safety validation before and after AI generation.

Responsibilities

- Crisis Detection
- Diagnosis Detection
- Greeting Detection
- Acknowledgement Detection
- Escalation Decision

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import re

from dataclasses import dataclass


@dataclass
class SafetyResult:

    safe: bool

    should_escalate: bool

    response: str | None = None

    reason: str | None = None


class SafetyService:

    CRISIS_PATTERNS = [

        r"\bkill myself\b",
        r"\bsuicide\b",
        r"\bend my life\b",
        r"\bwant to die\b",
        r"\bself harm\b",
        r"\bhurt myself\b",
        r"\bi don't want to live\b",

        r"\bmagpapakamatay\b",
        r"\bayoko nang mabuhay\b",
        r"\bpapatayin ko ang sarili ko\b",
        r"\bsaktan ang sarili\b",
    ]

    DIAGNOSIS_PATTERNS = [

        r"\bdo i have depression\b",
        r"\bdo i have anxiety\b",
        r"\bam i depressed\b",
        r"\bdiagnose me\b",

        r"\bmay depression ba ako\b",
        r"\bmay anxiety ba ako\b",
        r"\bdiagnose\b",
    ]

    GREETINGS = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "kumusta",
        "kamusta",
        "hello po",
        "hi po",
    }

    ACKNOWLEDGEMENTS = {
        "thanks",
        "thank you",
        "thank you so much",
        "salamat",
        "salamat po",
        "ok",
        "okay",
        "noted",
    }

    def check(
        self,
        message: str,
    ) -> SafetyResult:

        text = message.lower().strip()

        if self._is_crisis(text):

            return SafetyResult(
                safe=False,
                should_escalate=True,
                reason="crisis",
                response=(
                    "I'm really sorry you're going through this. "
                    "Please contact the Guidance Office immediately "
                    "or reach out to someone you trust. "
                    "If you are in immediate danger, "
                    "please contact your local emergency services."
                ),
            )

        if self._asks_for_diagnosis(text):

            return SafetyResult(
                safe=False,
                should_escalate=True,
                reason="diagnosis",
                response=(
                    "I'm not able to diagnose mental health conditions. "
                    "I encourage you to speak with a licensed guidance "
                    "counselor for proper support."
                ),
            )

        if self._is_greeting(text):

            return SafetyResult(
                safe=True,
                should_escalate=False,
                reason="greeting",
                response=(
                    "Hello! I'm CTRL4, the Guidance Office AI Assistant. "
                    "How may I assist you today?"
                ),
            )

        if self._is_acknowledgement(text):

            return SafetyResult(
                safe=True,
                should_escalate=False,
                reason="acknowledgement",
                response=(
                    "You're welcome! If you have any other questions, "
                    "I'm here to help."
                ),
            )

        return SafetyResult(
            safe=True,
            should_escalate=False,
        )

    def _is_crisis(
        self,
        text: str,
    ) -> bool:

        return any(
            re.search(pattern, text)
            for pattern in self.CRISIS_PATTERNS
        )

    def _asks_for_diagnosis(
        self,
        text: str,
    ) -> bool:

        return any(
            re.search(pattern, text)
            for pattern in self.DIAGNOSIS_PATTERNS
        )

    def _is_greeting(
        self,
        text: str,
    ) -> bool:

        return text in self.GREETINGS

    def _is_acknowledgement(
        self,
        text: str,
    ) -> bool:

        return text in self.ACKNOWLEDGEMENTS