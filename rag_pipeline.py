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
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
    except Exception:
        return -1
    
    def chunk_text(text, chunk_size=500, overlap=10):
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start+chunk_size])
            start+=chunk_size-overlap
        return chunks

    chunks = chunk_text(text)
    
    try:
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
    except Exception:
        return -1
    
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

    try:
        ans = check_groundedness(question, results['documents'][0])
    except Exception:
        return "Unable to process your question right now — please try again in a moment."
    
    if ans == True:
        prompt = f'Answer the question using ONLY this context. Say which part you used.\n\nContext:\n{context}\n\nQuestion: {question}'
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception:
            return "Unable to process your question right now — please try again in a moment."
    else:
        return "This document does not contain enough information to answer this question."
    

def check_groundedness(question, chunks):
    context = '\n\n'.join(chunks)
    prompt = f'''Given this context, determine if there is enough information to answer the question.
    
    Context:
    {context}

    Question: {question}

    Respond with ONLY "YES" if there is enough information, or "NO" if there is not enough information. Do not explain, just respond with YES or NO.'''
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    answer = response.text.strip().upper()
    
    return answer == "YES"