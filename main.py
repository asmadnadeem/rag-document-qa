import pdfplumber
with pdfplumber.open('test.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)