# query_pdf.py
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

load_dotenv()

client = OpenAI()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

def ask_question(query, collection_name, chat_history=None):
    if chat_history is None:
        chat_history = []

    vector_db = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name=collection_name,
        embedding=embedding_model
    )

    search_results = vector_db.similarity_search(query=query)

    context = "\n\n\n".join([
        f"Page Content: {r.page_content}\nPage Number: {r.metadata.get('page_label', '?')}" for r in search_results
    ])

    SYSTEM_PROMPT = f"""
You are a helpful assistant answering questions based ONLY on the following PDF content.
If unsure, tell the user where to look based on page number.
You must use the provided context to answer the question.
You can give the short summary of the context, but do not make up any information.

Context:
{context}
"""

    # Build the message list including system prompt and conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add previous chat history (user & assistant messages)
    for user_msg, bot_msg in chat_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    # Add current user query
    messages.append({"role": "user", "content": query})

    chat_completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )
    return chat_completion.choices[0].message.content

