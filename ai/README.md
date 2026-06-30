# Legacy AI Archive

Associated Thesis Title: Development of an AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

This folder is an archived copy of the earlier thesis prototype AI assets.

## Archive Scope

- `chatbot_ai.py`
- `dataset.csv`
- `english_stopwords.txt`
- `goemotions_1.csv`
- `tagalog_stopwords.txt`

## Important Note

These files are **legacy reference only** and are **not used** by the current chatbot runtime.

The active AI setup is now in the backend RAG pipeline:

- `backend/server/service.py`
- `backend/knowledge_base/`
- `backend/data/rag_index/`
- `backend/scripts/ingest_guidance_docs.py`

The current backend also includes active NLP-based negative emotion detection for escalation.

## Team Guidance

- Do not add new production chatbot logic in this folder.
- Add/update official chatbot knowledge in `backend/knowledge_base/`.
- Rebuild index after corpus changes by running:

```bash
cd backend
source .venv/bin/activate
python scripts/ingest_guidance_docs.py
```
