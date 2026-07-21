# RAG Document Intelligence System

A retrieval-augmented generation system that lets users upload any PDF and ask questions in natural language. Answers are grounded strictly in the document's content — a built-in verification step checks whether retrieved context is actually sufficient before generating a response, and explicitly declines rather than hallucinating when it isn't.

Built from scratch in Python — no LangChain in the core pipeline — to develop a complete understanding of how RAG systems work internally, from chunking and embeddings through retrieval, verification, and generation.

**Live demo:** https://rag-frontend-12gx.onrender.com
*(Free tier — first load after inactivity may take 30-60 seconds to wake up)*

**Backend API docs:** https://rag-backend-e3lz.onrender.com/docs

---

## What it does

1. Upload a PDF through a chat-style web interface
2. The document is extracted, chunked, and converted into vector embeddings
3. Embeddings are stored in ChromaDB, tagged by document ID for multi-document isolation
4. Ask a question — the system retrieves the most relevant chunks by semantic similarity
5. A groundedness check verifies the retrieved context actually contains enough information to answer
6. If sufficient, Gemini generates a cited answer. If not, the system explicitly says so instead of guessing
7. Full conversation displayed in a persistent chat interface

---

## Architecture

```
Streamlit Frontend (frontend.py)  ──── Render service #1
        │ HTTPS requests
        ▼
FastAPI Backend (api.py)  ──── Render service #2
        │
   ┌────┴────┐
   ▼         ▼
PostgreSQL   RAG Pipeline (rag_pipeline.py)
(Supabase)      │        │
 metadata        ▼        ▼
              ChromaDB   Gemini API
              (vectors)  (embeddings + generation)
```

Frontend and backend are fully decoupled, independently deployed services communicating over HTTPS — the backend API is a standalone service any client could consume, not just the interface built on top of it.

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
| Containerization | Docker | Two independent containers (backend, frontend) |
| Deployment | Render | Two independently hosted web services |

---

## Key Engineering Decisions

**Manual RAG pipeline, not LangChain.** Built chunking, embedding, retrieval, and prompt construction from scratch to understand the internals — LangChain would have abstracted away the exact mechanics this project was meant to teach.

**Groundedness verification before generation.** A separate Gemini call checks whether retrieved context is actually sufficient before an answer is generated. If not, the system explicitly declines rather than guessing — a real technique used to reduce hallucination in production RAG systems.

**Multi-document isolation via metadata tagging.** Every chunk stored in ChromaDB is tagged with its source document's ID, and retrieval queries are filtered accordingly — preventing cross-document contamination in results.

**PostgreSQL and ChromaDB split by responsibility.** Structured metadata (filenames, timestamps, status) lives in PostgreSQL, built for exact-match queries. Vector similarity search lives in ChromaDB, purpose-built for that — using the right tool for each kind of data rather than forcing one database to do both jobs.

**Fail-fast error handling.** Every endpoint validates input before doing expensive work — wrong file types, empty files, unparseable PDFs, invalid document references, empty questions, and Gemini API failures are all caught early with clear error messages instead of unhandled crashes.

**Two independent Docker containers, not one.** Backend and frontend are deployed as separate services communicating over HTTP, mirroring real client-server architecture — the backend has no knowledge of or dependency on the frontend, and could serve a mobile app or another website exactly as easily.

---

## Known Limitations

- **Synchronous processing** — `/upload` blocks until the entire document is embedded, which can take minutes for large PDFs. A production version would use a background task queue.
- **Conversation history is currently display-only** — the frontend shows chat history, but the backend treats each question independently and does not use prior messages as context for follow-ups.
- **ChromaDB runs as local persistent storage on the backend container** — this does not scale across multiple horizontally-scaled server instances; a production deployment would need a centrally hosted vector database.
- **Free-tier cold starts** — both services spin down after 15 minutes of inactivity; first request after idle time takes 30-60 seconds.
- **No OCR support** for scanned or image-only PDFs.
- **No password-protected PDF support.**

These are documented rather than fixed to reflect deliberate scope decisions within the project timeline, prioritized by actual impact on core functionality.

---

## Running Locally

```bash
# Clone and set up environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements-backend.txt
pip install -r requirements-frontend.txt

# Add to .env
GEMINI_API_KEY=your_key_here
DATABASE_URL=your_supabase_connection_string

# Terminal 1 — backend
uvicorn api:app --reload

# Terminal 2 — frontend
streamlit run frontend.py
```

Or with Docker Compose (requires virtualization enabled):
```bash
docker compose up --build
```

---

## Project Structure

```
rag-project/
├── main.py                     # Week 1: standalone RAG pipeline script
├── rag_pipeline.py              # Core RAG logic — chunking, embedding, retrieval, groundedness check
├── api.py                        # FastAPI backend — endpoints, validation, database
├── frontend.py                    # Streamlit chat interface
├── Dockerfile                      # Backend container
├── Dockerfile.frontend              # Frontend container
├── docker-compose.yml                # Local multi-container orchestration
├── requirements-backend.txt
├── requirements-frontend.txt
├── .env                                # Not committed
└── .gitignore
```

---

## Author

**Asmad Nadeem** · BSCS @ FAST-NUCES CFD
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/asmadnadeem)