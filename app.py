import streamlit as st
from ingest import index_pdf
from query import ask_question
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

from streamlit.runtime.scriptrunner import RerunException, RerunData

def rerun():
    raise RerunException(RerunData())

st.set_page_config(page_title="📄 ChatPDF Clone", layout="wide")
st.title("🤖 Chat with Your PDF")

# Upload PDF and prepare collection
uploaded_file = st.file_uploader("📄 Upload your PDF", type="pdf")

if uploaded_file is not None:
    pdf_name = uploaded_file.name.replace(".pdf", "").replace(" ", "_").lower()
    collection_name = f"pdf_{pdf_name}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        temp_pdf_path = tmp.name

    if st.button("📚 Prepare this PDF"):
        with st.spinner("Indexing..."):
            index_pdf(temp_pdf_path, collection_name)
            st.session_state['ready'] = True
            st.session_state['collection_name'] = collection_name
            st.success("✅ PDF is ready! You can now chat.")

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'ready' not in st.session_state:
    st.session_state['ready'] = False

if 'collection_name' not in st.session_state:
    st.session_state['collection_name'] = None

st.title("RAG PDF Chatbot with Multi-turn")

if not st.session_state['ready']:
    st.info("Upload and prepare a PDF first.")
else:
    user_input = st.text_area("Ask a question about the PDF:", height=100)

    if st.button("Send"):
        if user_input.strip():
            with st.spinner("Thinking..."):
                bot_response = ask_question(user_input, st.session_state['collection_name'], st.session_state.chat_history)
                st.session_state.chat_history.append((user_input, bot_response))
                rerun()

    # Display chat history
    for user_msg, bot_msg in st.session_state.chat_history:
        st.markdown(f"**You:** {user_msg}")
        st.markdown(f"**Bot:** {bot_msg}")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        rerun()
