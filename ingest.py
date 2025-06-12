# ingest_pdf.py
from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

def index_pdf(pdf_path, collection_name):
    loader = PyPDFLoader(file_path=pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    split_docs = splitter.split_documents(documents=docs)

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        url="http://localhost:6333",
        collection_name=collection_name,
        embedding=embedding_model
    )

    return True
