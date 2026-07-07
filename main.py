import os
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
