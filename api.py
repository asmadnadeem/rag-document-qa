import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile
app = FastAPI()
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))

@app.post("/upload")
async def upload_pdf(file: UploadFile):
    contents = await file.read()
    return {
        "filename": file.filename,
        "status": "received",
        "size": len(contents)
        }

@app.post('/query')
async def ask_question(question: str):
    return {
        'answer': 'placeholder — will connect RAG here'
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