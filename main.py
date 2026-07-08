import os
import chromadb
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
import pdfplumber
import time

with pdfplumber.open('test.pdf') as pdf:
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

embedded_chunks = []
for chunk in chunks:
    result = client.models.embed_content(model='gemini-embedding-001', contents=chunk)
    embedded_chunks.append({'text': chunk, 'embedding': result.embeddings[0].values})
    time.sleep(1)

chroma_client = chromadb.Client()
collection = chroma_client.create_collection('my_docs')

for i, item in enumerate(embedded_chunks):
    collection.add(documents=[item['text']], embeddings=[item['embedding']], ids=[f'chunk_{i}'])

question = 'what year was the research conducted?'
q_result = client.models.embed_content(model='gemini-embedding-001', contents=question)
q_embedding = q_result.embeddings[0].values
results = collection.query(query_embeddings=[q_embedding], n_results=3)

context = '\n\n'.join(results['documents'][0])
prompt = f'Answer the question using ONLY this context. Say which part you used.\n\nContext:\n{context}\n\nQuestion: {question}'
response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
print(response.text)