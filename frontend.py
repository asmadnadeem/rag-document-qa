import streamlit as st
import requests

st.set_page_config(page_title="Document Intelligence", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lora&display=swap');

body {
    background-color: #3D3D2E;
}

.main {
    background-color: #3D3D2E;
}

section[data-testid="stMain"] {
    background-color: #3D3D2E;
}

h1 {
    font-family: 'Playfair Display', serif;
    color: #E8E2C4;
}

* {
    font-family: 'Lora', serif;
}
</style>
""", unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

st.title('ONE DOCUMENT. EVERY ANSWER.')
uploaded_file = st.file_uploader('Choose a PDF', type='pdf')

if uploaded_file:
    if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
        st.session_state.messages = []
        response = requests.post('http://backend:8000/upload', files={'file': uploaded_file})
        result = response.json()
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.document_id = result['document_id']
        st.success(f"Uploaded: {uploaded_file.name}")

if question := st.chat_input('Ask about your document'):
    st.session_state.messages.append({'role': 'user', 'content': question})
    with st.chat_message('user'):
        st.write(question)
    
    with st.spinner('Thinking...'):
        response = requests.post('http://backend:8000/query', params={'question': question, 'document_id': st.session_state.document_id})
        answer = response.json()['answer']
    
    st.session_state.messages.append({'role': 'assistant', 'content': answer})
    with st.chat_message('assistant'):
        st.write(answer)