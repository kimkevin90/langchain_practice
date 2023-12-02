import random
from langchain.chat_models import ChatOpenAI
from app.chat.models import ChatArgs
from app.chat.vector_stores import retriever_map
from app.chat.llms import llm_map
from app.chat.memories import memory_map
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain
from app.web.api import (
    set_conversation_components,
    get_conversation_components
)
from app.chat.score import random_component_by_score

def select_component(
    component_type, component_map, chat_args
):
    components = get_conversation_components(
        chat_args.conversation_id
    )
    previous_component = components[component_type]

    if previous_component:
        builder = component_map[previous_component]
        return previous_component, builder(chat_args)
    else:
        # 새로운 대화 시작 시, score가 높은 compoent 구성 요소 적용
        random_name = random_component_by_score(component_type, component_map)
        builder = component_map[random_name]
        return random_name, builder(chat_args)


def build_chat(chat_args: ChatArgs):
    """
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: A chain

    Example Usage:

        chain = build_chat(chat_args)
    """

    retriever_name, retriever = select_component(
        "retriever",
        retriever_map,
        chat_args
    )

    llm_name, llm = select_component(
        "llm",
        llm_map,
        chat_args
    )
    memory_name, memory = select_component(
        "memory",
        memory_map,
        chat_args
    )

    print(
        f"Running chain with: memory {memory_name}, llm: {llm_name}, retriever: {retriever_name}"
    )
    set_conversation_components(
        chat_args.conversation_id,
        llm=llm_name,
        retriever=retriever_name,
        memory=memory_name
    )
    

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