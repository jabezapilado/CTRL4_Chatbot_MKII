"""
AI Service

Main AI orchestration service for CTRL4 Chatbot MK2.

Responsibilities

- Safety Validation
- Language Detection
- Emotion Detection
- Knowledge Retrieval (RAG)
- Prompt Construction
- LLM Response Generation

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import traceback
import time

from dataclasses import dataclass

from .emotion_service import EmotionService
from .language_service import LanguageService
from .rag_service import RAGService
from .prompt_builder import PromptBuilder, PromptInput
from .llm_service import LLMService
from .safety_service import SafetyService


@dataclass
class ChatResponse:

    success: bool

    response: str

    emotion: str

    sentiment: str

    language: str

    escalated: bool

    confidence: float


class AIService:

    def __init__(
        self,
        safety: SafetyService | None = None,
        language: LanguageService | None = None,
        emotion: EmotionService | None = None,
        rag: RAGService | None = None,
        prompt_builder: PromptBuilder | None = None,
        llm: LLMService | None = None,
    ):

        self.safety = safety or SafetyService()

        self.language = language or LanguageService()

        self.emotion = emotion or EmotionService()

        self.rag = rag or RAGService()

        self.prompt_builder = prompt_builder or PromptBuilder()

        self.llm = llm or LLMService()

    def respond(
        self,
        message: str,
        conversation: list[dict] | None = None,
    ) -> ChatResponse:

        if conversation is None:
            conversation = []
        
        # -----------------------------------------
        # Performance Tracking
        # -----------------------------------------

        pipeline_start = time.perf_counter()

        def print_pipeline():
            total_time = time.perf_counter() - pipeline_start
            print("=" * 60)
            print("CTRL4 AI Pipeline Performance")
            print("=" * 60)
            print(f"Safety Check      : {safety_time:.3f}s")
            print(f"Language Detect   : {language_time:.3f}s")
            print(f"Emotion Detect    : {emotion_time:.3f}s")
            print(f"RAG Retrieval     : {rag_time:.3f}s")
            print(f"Prompt Builder    : {prompt_time:.3f}s")
            print(f"LLM Generation    : {llm_time:.3f}s")
            print("-" * 60)
            print(f"Total Pipeline    : {total_time:.3f}s")
            print("=" * 60)
            
        try:

            # -----------------------------------------
            # Safety Validation
            # -----------------------------------------

            safety_start = time.perf_counter()
            safety = self.safety.check(message)
            safety_time = time.perf_counter() - safety_start

            if safety.response:

                return ChatResponse(
                    success=True,
                    response=safety.response,
                    emotion="Unknown",
                    sentiment="Unknown",
                    language="Unknown",
                    escalated=safety.should_escalate,
                    confidence=0.0,
                )

            # -----------------------------------------
            # Language Detection
            # -----------------------------------------

            language_start = time.perf_counter()
            language = self.language.detect(message)
            language_time = time.perf_counter() - language_start

            # -----------------------------------------
            # Emotion Detection
            # -----------------------------------------

            emotion_start = time.perf_counter()
            emotion = self.emotion.predict(message)
            emotion_time = time.perf_counter() - emotion_start

            # -----------------------------------------
            # Knowledge Retrieval
            # -----------------------------------------

            rag_start = time.perf_counter()
            documents = []

            if self.rag.ready:
                documents = self.rag.retrieve(message)
                
            rag_time = time.perf_counter() - rag_start

            # -----------------------------------------
            # Prompt Construction
            # -----------------------------------------

            prompt_start = time.perf_counter()
            prompt = self.prompt_builder.build(

                PromptInput(

                    message=message,

                    conversation=conversation,

                    emotion=emotion,

                    language=language,

                    documents=documents,
                )

            )
            prompt_time = time.perf_counter() - prompt_start

            # -----------------------------------------
            # LLM Response Generation
            # -----------------------------------------

            llm_start = time.perf_counter()
            llm = self.llm.generate(prompt)
            llm_time = time.perf_counter() - llm_start

            print_pipeline()
            
            if not llm.success:
                
                print("=" * 60)
                print("LLM Error")
                print("=" * 60)
                print(f"Provider : {self.llm.provider_name}")
                print(f"Error    : {llm.error}")
                print("=" * 60)

                return ChatResponse(

                    success=False,

                    response=(
                        "I'm sorry, but I'm currently unable "
                        "to generate a response. "
                        "Please try again later."
                    ),

                    emotion=emotion.emotion,

                    sentiment=emotion.sentiment,

                    language=language.language,

                    escalated=emotion.is_negative,

                    confidence=emotion.confidence,
                )

            # -----------------------------------------
            # Final Response
            # -----------------------------------------
            
            return ChatResponse(

                success=True,

                response=llm.text,

                emotion=emotion.emotion,

                sentiment=emotion.sentiment,

                language=language.language,

                escalated=(
                    safety.should_escalate
                    or emotion.is_negative
                ),

                confidence=emotion.confidence,
            )

        except Exception as exception:

            print("=" * 60)
            print("AIService Exception")
            print("=" * 60)
            print(f"Message: {message}")
            print(f"Exception: {exception}")

            traceback.print_exc()

            print("=" * 60)

            return ChatResponse(
                success=False,
                response=(
                    "An unexpected error occurred while "
                    "processing your request."
                ),
                emotion="Unknown",
                sentiment="Unknown",
                language="Unknown",
                escalated=False,
                confidence=0.0,
            )