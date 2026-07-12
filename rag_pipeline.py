import os
import io
import time
import pdfplumber
import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
chroma_client = chromadb.PersistentClient(path='./chroma_db')
collection = chroma_client.get_or_create_collection('my_docs')

def process_pdf(file_bytes, document_id):
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    
    def chunk_text(text, chunk_size=500, overlap=10):
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start+chunk_size])
            start+=chunk_size-overlap
        return chunks

    chunks = chunk_text(text)
    
    for i, chunk in enumerate(chunks):
        result = client.models.embed_content(model='gemini-embedding-001', contents=chunk)
        embedding = result.embeddings[0].values
        
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f'doc{document_id}_chunk{i}'],
            metadatas=[{"document_id": document_id}]
        )
        time.sleep(1)
    
    return len(chunks)

def answer_question(question, document_id):
    q_result = client.models.embed_content(model='gemini-embedding-001', contents=question)
    q_embedding = q_result.embeddings[0].values
    
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=3,
        where={"document_id": document_id}
    )
    
    context = '\n\n'.join(results['documents'][0])
    
    prompt = f'Answer the question using ONLY this context. Say which part you used.\n\nContext:\n{context}\n\nQuestion: {question}'
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    
    return response.text