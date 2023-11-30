from langchain.chains import ConversationalRetrievalChain
from app.chat.models import ChatArgs
from app.chat.vector_stores.pinecone import build_retriever
from app.chat.llms.chatopenai import build_llm
from app.chat.memories.sql_memory import build_memory

def build_chat(chat_args: ChatArgs):
    """
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: A chain

    Example Usage:

        chain = build_chat(chat_args)
    """
    retriever = build_retriever(chat_args)
    llm = build_llm(chat_args)
    memory = build_memory(chat_args)

    # ConversationalRetrievalChain을 사용하여 대화형 검색 체인을 구성하는 과정을 보여줍니다. 
    # 이 체인은 검색(retriever), 언어 모델(llm), 그리고 메모리 시스템(memory)을 통합하여 사용자의 질문에 답변을 생성합니다.
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        retriever=retriever
    )