import random
from langchain.chat_models import ChatOpenAI
from app.chat.models import ChatArgs
from app.chat.vector_stores import retriever_map
from app.chat.llms.chatopenai import build_llm
from app.chat.memories.sql_memory import build_memory
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain
from app.web.api import (
    set_conversation_components,
    get_conversation_components
)

def build_chat(chat_args: ChatArgs):
    """
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: A chain

    Example Usage:

        chain = build_chat(chat_args)
    """
    components = get_conversation_components(
        chat_args.conversation_id
    )
    previous_retriever = components["retriever"]

    retriever = None
    if previous_retriever:
        # DB에 저장된 retriever 사용
        build_retriever = retriever_map[previous_retriever]
        retriever = build_retriever(chat_args)
    else:
        # 무작위 retriever 생성 후 사용
        random_retriever_name = random.choice(list(retriever_map.keys()))
        build_retriever = retriever_map[random_retriever_name]
        retriever = build_retriever(chat_args)
        set_conversation_components(
            conversation_id=chat_args.conversation_id,
            llm="",
            memory="",
            retriever=random_retriever_name
        )


    retriever = build_retriever(chat_args)
    llm = build_llm(chat_args)
    memory = build_memory(chat_args)

    # ConversationalRetrievalChain을 사용하여 대화형 검색 체인을 구성하는 과정을 보여줍니다. 
    # 이 체인은 검색(retriever), 언어 모델(llm), 그리고 메모리 시스템(memory)을 통합하여 사용자의 질문에 답변을 생성합니다.
    # return ConversationalRetrievalChain.from_llm(
    #     llm=llm,
    #     memory=memory,
    #     retriever=retriever
    # )

    condense_question_llm = ChatOpenAI(streaming=False)

    # 스트리밍을 위해 기존의 ConversationalRetrievalChain과 StreamableChain을 연결
    # condense_question_llm streaming=False로 설정하여 condense_question_chain시에는 미발동 적용
    return StreamingConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        condense_question_llm=condense_question_llm,
        retriever=retriever
    )