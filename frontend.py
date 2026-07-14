import streamlit as st
import requests

st.title('Document Q&A System')
uploaded_file = st.file_uploader('Choose a PDF', type='pdf')

if uploaded_file:
    if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
        response = requests.post('http://localhost:8000/upload', files={'file': uploaded_file})
        result = response.json()
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.document_id = result['document_id']
        st.success(f"Uploaded: {uploaded_file.name}")

st.subheader('Ask a Question')
question = st.text_input('Your question')

if st.button('Ask') and question:
    response = requests.post('http://localhost:8000/query', params={'question': question, 'document_id': st.session_state.document_id})
    st.write(response.json()['answer'])