# RAG Document Intelligence System

A retrieval-augmented generation system that lets users upload any PDF and ask questions in natural language — answers are grounded strictly in the document's content, with a built-in verification step that refuses to answer rather than hallucinate when the document doesn't contain enough information.

Built from scratch in Python — no LangChain in the core pipeline — to develop a full understanding of how RAG systems work internally, from chunking and embeddings through retrieval, verification, and generation.

---

## Live Demo

[Coming in Week 4 — deployment in progress]

---

## What it does

1. Upload a PDF through a chat-style web interface
2. The document is extracted, chunked, and converted into vector embeddings
3. Embeddings are stored in ChromaDB, tagged by document for multi-document isolation
4. Ask a question — the system retrieves the most relevant chunks by semantic similarity
5. A groundedness check verifies the retrieved context actually contains enough information to answer
6. If sufficient, Gemini generates a cited answer. If not, the system explicitly says so instead of guessing
7. Full conversation displayed in a persistent chat interface

---

## Architecture

```
Streamlit Frontend (frontend.py)
        ↓ HTTP requests
FastAPI Backend (api.py)
        ↓
    ┌───┴────┐
    ↓        ↓
PostgreSQL   RAG Pipeline (rag_pipeline.py)
(metadata)      ↓        ↓
              ChromaDB   Gemini API
              (vectors)  (embeddings + generation)
```

Frontend and backend are fully decoupled — the FastAPI backend can be consumed by any client (web, mobile, another service) through its documented endpoints, independent of the Streamlit interface built on top of it.

---

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Frontend | Streamlit | Chat-based web interface |
| Backend | FastAPI | REST API — upload and query endpoints |
| Metadata Storage | PostgreSQL (Supabase) | Document records, structured queries |
| Vector Storage | ChromaDB | Embedding storage and similarity search |
| Embeddings & Generation | Google Gemini API | `gemini-embedding-001`, `gemini-2.5-flash` |
| PDF Processing | pdfplumber | Text extraction |

---

## Key Engineering Decisions

**Manual RAG pipeline, not LangChain.** Built chunking, embedding, retrieval, and prompt construction from scratch to understand the internals — LangChain would have abstracted away the exact mechanics this project was meant to teach.

**Groundedness verification, not hallucination-prone generation.** Before generating an answer, a separate Gemini call checks whether retrieved context is actually sufficient. If not, the system explicitly declines rather than guessing — a real technique used to reduce hallucination in production RAG systems.

**Multi-document isolation via metadata tagging.** Every chunk stored in ChromaDB is tagged with its source document's ID, and queries are filtered accordingly — preventing cross-document contamination in retrieval results.

**PostgreSQL and ChromaDB split by responsibility.** Structured metadata (filenames, timestamps, status) lives in PostgreSQL, which is built for exact-match queries. Vector similarity search lives in ChromaDB, which is purpose-built for that — using the right tool for each kind of data.

**Fail-fast error handling.** Every endpoint validates input before doing expensive work — wrong file types, empty files, unparseable PDFs, invalid document references, and empty questions are all caught early with clear error messages instead of unhandled crashes.

---

## Known Limitations

- **Synchronous processing** — `/upload` blocks until the entire document is embedded, which can take minutes for large PDFs. A production version would use a background task queue.
- **Conversation history is currently display-only** — the frontend shows chat history, but the backend treats each question independently and does not use prior messages as context for follow-ups.
- **ChromaDB runs as local persistent storage** — this does not scale across multiple horizontally-scaled server instances; a production deployment would need a centrally hosted vector database.
- **No OCR support** — scanned or image-only PDFs will return no extractable text.
- **No password-protected PDF support.**

These are documented rather than fixed to reflect deliberate scope decisions within the project timeline — prioritized by actual impact on core functionality.

---

## Running Locally

```bash
# Clone and set up environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install pdfplumber google-genai python-dotenv chromadb fastapi uvicorn python-multipart psycopg2-binary sqlalchemy streamlit

# Add to .env
GEMINI_API_KEY=your_key_here
DATABASE_URL=your_supabase_connection_string

# Terminal 1 — backend
uvicorn api:app --reload

# Terminal 2 — frontend
streamlit run frontend.py
```

---

## Project Structure

```
rag-project/
├── main.py            # Week 1: standalone RAG pipeline script
├── rag_pipeline.py     # Core RAG logic — chunking, embedding, retrieval, groundedness check
├── api.py               # FastAPI backend — endpoints, validation, database
├── frontend.py           # Streamlit chat interface
├── requirements.txt
├── .env                  # Not committed
└── .gitignore
```

---

## Author

**Asmad Nadeem** · BSCS @ FAST-NUCES CFD
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/asmadnadeem)