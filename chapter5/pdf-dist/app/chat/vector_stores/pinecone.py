import os
import pinecone
from langchain.vectorstores import Pinecone
from app.chat.embeddings.openai import embeddings

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV_NAME")
)

vector_store = Pinecone.from_existing_index(
    os.getenv("PINECONE_INDEX_NAME"), embeddings
)

# vector_store.as_retriever()

# chat_args를 받아, 벡터스토어에서 pdf_id를 찾아 retriever 반환
def build_retriever(chat_args):
    search_kwargs = {"filter": { "pdf_id": chat_args.pdf_id }}
    return vector_store.as_retriever(
        search_kwargs=search_kwargs
    )