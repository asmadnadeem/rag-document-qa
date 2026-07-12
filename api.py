import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, HTTPException
app = FastAPI()
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))
from rag_pipeline import process_pdf, answer_question

@app.post("/upload")
async def upload_pdf(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file attached")
    
    with engine.connect() as conn:
        result = conn.execute(
        text("INSERT INTO documents (filename, file_size, status) VALUES (:filename, :file_size, :status) RETURNING id"),
        {"filename": file.filename, "file_size": len(contents), "status": "uploaded"}
        )
        document_id = result.fetchone()[0]
        conn.commit()

    num_chunks = process_pdf(contents, document_id)

    if num_chunks == 0:
        raise HTTPException(status_code=400, detail="NO text detected on PDF")
    
    return {
        "filename": file.filename,
        "status": "received",
        "size": len(contents)
        }

@app.post('/query')
async def ask_question(question: str, document_id: int):
    if question.strip() == "":
        raise HTTPException(status_code=400, detail="Empty question")
    
    with engine.connect() as conn:
        result = conn.execute(
        text("SELECT id FROM documents WHERE id = :document_id"),
        {"document_id": document_id}
        )
        document = result.fetchone()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    answer = answer_question(question, document_id)
    return {
        'answer': answer
        }

def create_tables():
    with engine.connect() as conn:
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        upload_date TIMESTAMP DEFAULT NOW(),
        file_size INTEGER,
        status TEXT
        )
        '''))
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS chunks (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        chunk_text TEXT,
        chunk_index INTEGER
        )
        '''))
        conn.commit()

create_tables()