from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .config import Config


def _safe_import_langdetect_detect():
    try:
        from langdetect import detect  # type: ignore

        return detect
    except Exception:
        return None


CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bsuicide\b",
    r"\bwant to die\b",
    r"\bself[- ]?harm\b",
    r"\bsaktan ang sarili\b",
    r"\bmagpakamatay\b",
    r"\bwala nang dahilan\b",
    r"\bhindi ko na kaya\b",
]

DIAGNOSIS_PATTERNS = [
    r"\bdiagnos(e|is)\b",
    r"\bmay depression ba ako\b",
    r"\bdo i have depression\b",
    r"\bmental disorder\b",
    r"\banxiety disorder\b",
]

NEGATIVE_EMOTION_TERMS = {
    "english": {
        "sad": 0.25,
        "hopeless": 0.40,
        "anxious": 0.30,
        "anxiety": 0.30,
        "panic": 0.35,
        "overwhelmed": 0.35,
        "stressed": 0.25,
        "depressed": 0.40,
        "lonely": 0.25,
        "burnout": 0.30,
        "worthless": 0.45,
        "tired of everything": 0.45,
        "cant cope": 0.40,
        "can't cope": 0.40,
        "not okay": 0.25,
        "i feel empty": 0.40,
    },
    "tagalog": {
        "malungkot": 0.25,
        "pagod na pagod": 0.35,
        "sobrang pagod": 0.30,
        "naiiyak": 0.30,
        "nahihirapan": 0.30,
        "hindi ko kaya": 0.45,
        "hindi ko na kaya": 0.55,
        "wala akong gana": 0.30,
        "natatakot": 0.25,
        "nag-aalala": 0.25,
        "nag aalala": 0.25,
        "kinakabahan": 0.25,
        "nalulunod": 0.40,
        "gulong gulo": 0.30,
        "walang pag-asa": 0.45,
        "walang pag asa": 0.45,
        "hindi ako okay": 0.30,
        "di ako okay": 0.30,
    },
}

DISTRESS_INTENSIFIERS = {
    "very": 0.10,
    "so": 0.08,
    "super": 0.10,
    "sobra": 0.10,
    "sobrang": 0.10,
    "grabe": 0.10,
    "talaga": 0.05,
    "really": 0.08,
}


@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float


@dataclass
class ChatResult:
    response: str
    emotion: str
    escalate: bool
    category: str
    confidence: float


def normalize_text(text: str) -> str:
    lowered = str(text).strip().lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        if end < len(text):
            split_at = max(chunk.rfind("\n\n"), chunk.rfind(". "), chunk.rfind("? "), chunk.rfind("! "))
            if split_at > chunk_size // 3:
                end = start + split_at + 1
                chunk = text[start:end]
        chunks.append(chunk.strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)

    return [c for c in chunks if c]


def _extract_pdf_text(file_path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""

    pages: list[str] = []
    reader = PdfReader(str(file_path))
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _extract_docx_text(file_path: Path) -> str:
    try:
        from docx import Document  # type: ignore
    except Exception:
        return ""

    document = Document(str(file_path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def read_document_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_text(file_path)
    if suffix == ".docx":
        return _extract_docx_text(file_path)
    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    return ""


class MultilingualRAGService:
    def __init__(self) -> None:
        self.config = Config()
        self.docs_dir = Path(self.config.RAG_DOCS_DIR)
        self.index_dir = Path(self.config.RAG_INDEX_DIR)
        self.index_file = self.index_dir / "knowledge.faiss"
        self.metadata_file = self.index_dir / "metadata.json"
        self.embedding_model_name = self.config.RAG_EMBEDDING_MODEL

        self.embedder = None
        self.faiss = None
        self.index = None
        self.metadata: list[dict[str, Any]] = []
        self._detect_lang = _safe_import_langdetect_detect()
        self.generator = None
        self.generator_tokenizer = None
        self.initialization_error: str | None = None

        self._initialize_runtime()

    def _initialize_runtime(self) -> None:
        try:
            import faiss  # type: ignore
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception:
            self.initialization_error = (
                "RAG dependencies are missing. Install sentence-transformers and faiss-cpu."
            )
            return

        self.faiss = faiss
        self.embedder = SentenceTransformer(self.embedding_model_name)

        if self.config.RAG_GENERATOR_MODEL:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline  # type: ignore

                self.generator_tokenizer = AutoTokenizer.from_pretrained(self.config.RAG_GENERATOR_MODEL)
                model = AutoModelForCausalLM.from_pretrained(self.config.RAG_GENERATOR_MODEL)
                self.generator = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=self.generator_tokenizer,
                )
            except Exception:
                self.generator = None
                self.generator_tokenizer = None

        if self.index_file.exists() and self.metadata_file.exists():
            self._load_index()
            return

        if self.config.RAG_AUTO_BUILD_ON_START:
            self.build_index()

    def _build_embedding_input(self, text: str, is_query: bool) -> str:
        if "e5" in self.embedding_model_name.lower():
            return f"query: {text}" if is_query else f"passage: {text}"
        return text

    def _embed(self, texts: list[str], is_query: bool):
        if not self.embedder:
            raise RuntimeError("Embedding model is not available.")

        prepared = [self._build_embedding_input(text, is_query=is_query) for text in texts]
        return self.embedder.encode(prepared, normalize_embeddings=True, convert_to_numpy=True)

    def _load_index(self) -> None:
        if not self.faiss:
            return
        self.index = self.faiss.read_index(str(self.index_file))
        self.metadata = json.loads(self.metadata_file.read_text(encoding="utf-8"))

    def build_index(self) -> int:
        if not self.embedder or not self.faiss:
            return 0

        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        doc_paths = sorted(
            [
                path
                for path in self.docs_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in {".pdf", ".docx", ".txt", ".md"}
            ]
        )

        chunks: list[dict[str, Any]] = []
        for path in doc_paths:
            raw = read_document_text(path)
            clean = normalize_text(raw)
            if not clean:
                continue
            for idx, chunk in enumerate(
                split_text(
                    clean,
                    chunk_size=self.config.RAG_CHUNK_SIZE,
                    overlap=self.config.RAG_CHUNK_OVERLAP,
                )
            ):
                chunks.append(
                    {
                        "text": chunk,
                        "source": str(path.relative_to(self.docs_dir)),
                        "chunk_id": idx,
                    }
                )

        if not chunks:
            self.index = None
            self.metadata = []
            return 0

        vectors = self._embed([item["text"] for item in chunks], is_query=False)
        dim = int(vectors.shape[1])
        index = self.faiss.IndexFlatIP(dim)
        index.add(vectors)

        self.faiss.write_index(index, str(self.index_file))
        self.metadata_file.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

        self.index = index
        self.metadata = chunks
        return len(chunks)

    def _detect_language(self, text: str) -> str:
        text = normalize_text(text)
        if not text:
            return "unknown"

        has_tagalog_particles = any(token in text for token in [" po ", " naman", "paano", "kailangan", "ba "])
        has_english_tokens = any(token in text for token in [" how ", " where ", " guidance", "counseling", "appointment"])
        if has_tagalog_particles and has_english_tokens:
            return "taglish"

        if self._detect_lang:
            try:
                lang = self._detect_lang(text)
                if lang == "tl":
                    return "tagalog"
                if lang == "en":
                    return "english"
            except Exception:
                pass

        return "unknown"

    def _is_crisis(self, text: str) -> bool:
        lowered = normalize_text(text)
        return any(re.search(pattern, lowered) for pattern in CRISIS_PATTERNS)

    def _asks_for_diagnosis(self, text: str) -> bool:
        lowered = normalize_text(text)
        return any(re.search(pattern, lowered) for pattern in DIAGNOSIS_PATTERNS)

    def _score_negative_emotion(self, text: str) -> float:
        lowered = normalize_text(text)
        if not lowered:
            return 0.0

        score = 0.0
        for term_score in NEGATIVE_EMOTION_TERMS.values():
            for term, weight in term_score.items():
                if term in lowered:
                    score += weight

        for intensifier, weight in DISTRESS_INTENSIFIERS.items():
            if f" {intensifier} " in f" {lowered} ":
                score += weight

        if re.search(r"!{2,}|\?{2,}", text):
            score += 0.05

        if any(phrase in lowered for phrase in ["i feel", "i am", "ako ay", "pakiramdam ko", "feeling ko"]):
            score += 0.05

        return min(score, 1.0)

    def _build_contextual_query(self, message: str, conversation: list[dict[str, Any]] | None = None) -> str:
        if not conversation:
            return normalize_text(message)

        recent_user_turns = [
            str(turn.get("text", "")).strip()
            for turn in conversation[-6:]
            if str(turn.get("from", "")).lower() == "user" and str(turn.get("text", "")).strip()
        ]
        recent_user_turns = recent_user_turns[-2:]
        return normalize_text(" ".join(recent_user_turns + [message]))

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        if not self.embedder or not self.faiss or self.index is None or not self.metadata:
            return []

        query_vector = self._embed([query], is_query=True)
        k = max(1, self.config.RAG_TOP_K)
        scores, indices = self.index.search(query_vector, k)

        results: list[RetrievedChunk] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            if float(score) < self.config.RAG_MIN_SCORE:
                continue
            meta = self.metadata[int(idx)]
            results.append(
                RetrievedChunk(
                    text=str(meta.get("text", "")),
                    source=str(meta.get("source", "unknown")),
                    score=float(score),
                )
            )
        return results

    def _generate_grounded_response(self, retrieved: list[RetrievedChunk], language: str) -> str:
        if not retrieved:
            return (
                "I do not have enough official Guidance Office information to answer that yet. "
                "Please contact the SOC Guidance Office directly for verified assistance."
            )

        context_lines = []
        sources: list[str] = []
        for chunk in retrieved[:3]:
            context_lines.append(chunk.text)
            if chunk.source not in sources:
                sources.append(chunk.source)

        context = " ".join(context_lines)
        if self.generator:
            prompt = (
                "You are a school guidance assistant. Use only the provided context. "
                "If the context is insufficient, say you do not know.\n\n"
                f"Context:\n{context}\n\n"
                "Answer in the user's language (English, Tagalog, or Taglish)."
            )
            try:
                generated = self.generator(
                    prompt,
                    max_new_tokens=180,
                    do_sample=False,
                    temperature=0.0,
                )[0]["generated_text"]
                answer = generated[len(prompt):].strip()
                if answer:
                    source_note = f" Sources: {', '.join(sources[:2])}."
                    return f"{answer}{source_note}"
            except Exception:
                pass

        sentences = re.split(r"(?<=[.!?])\s+", context)
        answer = " ".join([s.strip() for s in sentences if s.strip()][:3]).strip()
        if not answer:
            answer = context[:600].strip()

        prefix = "Batay sa official Guidance Office documents: " if language in {"tagalog", "taglish"} else "Based on official Guidance Office documents: "
        source_note = f" Sources: {', '.join(sources[:2])}."
        return f"{prefix}{answer}{source_note}"

    def respond(self, message: str, conversation: list[dict[str, Any]] | None = None) -> ChatResult:
        if self.initialization_error:
            return ChatResult(
                response=(
                    "The multilingual RAG service is not fully initialized. "
                    "Please install NLP dependencies and build the knowledge index."
                ),
                emotion="neutral",
                escalate=False,
                category="system",
                confidence=0.0,
            )

        if self._is_crisis(message):
            return ChatResult(
                response=(
                    "I am sorry you are going through this. I cannot provide crisis counseling, "
                    "but your concern should be escalated immediately to the SOC Guidance Office. "
                    "If there is immediate danger, please contact local emergency services now."
                ),
                emotion="negative",
                escalate=True,
                category="escalation",
                confidence=1.0,
            )

        if self._asks_for_diagnosis(message):
            return ChatResult(
                response=(
                    "I cannot provide medical or psychological diagnosis. "
                    "Please consult a licensed counselor through the SOC Guidance Office."
                ),
                emotion="neutral",
                escalate=False,
                category="safety",
                confidence=1.0,
            )

        emotion_score = self._score_negative_emotion(message)
        if self.config.EMOTION_ESCALATION_ENABLED and emotion_score >= self.config.EMOTION_ESCALATION_THRESHOLD:
            return ChatResult(
                response=(
                    "Thank you for sharing this. It sounds emotionally heavy, and your message should be escalated "
                    "to the SOC Guidance Office so a counselor can support you as soon as possible. "
                    "If you are in immediate danger, contact emergency services now."
                ),
                emotion="negative",
                escalate=True,
                category="emotion_escalation",
                confidence=emotion_score,
            )

        language = self._detect_language(message)
        query = self._build_contextual_query(message, conversation)
        retrieved = self.retrieve(query)

        return ChatResult(
            response=self._generate_grounded_response(retrieved, language),
            emotion="neutral",
            escalate=False,
            category="guidance_rag",
            confidence=retrieved[0].score if retrieved else 0.0,
        )


@lru_cache(maxsize=1)
def get_chatbot_service() -> MultilingualRAGService:
    return MultilingualRAGService()
