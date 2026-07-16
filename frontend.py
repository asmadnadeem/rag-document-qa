import streamlit as st
import requests

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

st.title('Document Q&A System')
uploaded_file = st.file_uploader('Choose a PDF', type='pdf')

if uploaded_file:
    if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
        response = requests.post('http://localhost:8000/upload', files={'file': uploaded_file})
        result = response.json()
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.document_id = result['document_id']
        st.success(f"Uploaded: {uploaded_file.name}")

if question := st.chat_input('Ask about your document'):
    st.session_state.messages.append({'role': 'user', 'content': question})
    with st.chat_message('user'):
        st.write(question)
    
    with st.spinner('Thinking...'):
        response = requests.post('http://localhost:8000/query', params={'question': question, 'document_id': st.session_state.document_id})
        answer = response.json()['answer']
    
    st.session_state.messages.append({'role': 'assistant', 'content': answer})
    with st.chat_message('assistant'):
        st.write(answer)