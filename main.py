import pdfplumber

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

result = chunk_text(text)

print(len(result))
print(result[0])
print(result[1])