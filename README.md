# RAG Document Intelligence — Core Pipeline

A retrieval-augmented generation pipeline built from scratch in Python. Upload any PDF, ask a question in natural language, and get a cited answer drawn directly from the document — no hallucination, no guesswork.

---

## What it does

1. Extracts and cleans text from any PDF
2. Splits the document into overlapping chunks for semantic precision
3. Generates vector embeddings for each chunk via Google Gemini API
4. Stores embeddings in ChromaDB for fast similarity search
5. Embeds the user's question and retrieves the most relevant chunks
6. Sends retrieved context + question to Gemini and returns a cited answer

This is the foundation layer of a production RAG system — built without LangChain abstractions to ensure full understanding of the internals.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| PDF Extraction | pdfplumber |
| Text Chunking | Custom Python (chunk_size=500, overlap=10) |
| Embeddings | Google Gemini API (gemini-embedding-001) |
| Vector Storage | ChromaDB |
| Answer Generation | Google Gemini (gemini-2.5-flash) |
| Environment | python-dotenv |

---

## Project Structure

```
rag-project/
├── main.py          # Full RAG pipeline
├── .env             # API keys (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# 1. Clone the repo and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install pdfplumber google-genai python-dotenv chromadb

# 3. Add your Gemini API key to .env
GEMINI_API_KEY=your_key_here

# 4. Drop your PDF into the project folder and rename it test.pdf

# 5. Run
python main.py
```

---

## Architecture

```
PDF → Text Extraction → Chunking → Embedding → ChromaDB
                                                    ↓
Answer ← Gemini Generation ← Context Assembly ← Retrieval ← Question Embedding
```

---

## Author

**Asmad Nadeem** · BSCS @ FAST-NUCES CFD  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/asmadnadeem)