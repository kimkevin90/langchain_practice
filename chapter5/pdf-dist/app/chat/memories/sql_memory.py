from langchain.memory import ConversationBufferMemory
from app.chat.memories.histories.sql_history import SqlMessageHistory

from app.web.api import (
    # 유저A와의 채팅 내역 id
    get_messages_by_conversation_id,
    # 대화내역 db에 추가
    add_message_to_conversation
)

def build_memory(chat_args):
    # onversationBufferMemory: SqlMessageHistory 인스턴스를 메모리로 사용하여 대화 내용을 관리합니다.
    return ConversationBufferMemory(
        chat_memory=SqlMessageHistory(
            conversation_id=chat_args.conversation_id
        ),
        # return_messages=True는 메모리에서 메시지를 반환할지 여부를 결정합니다.
        return_messages=True,
        # memory_key="chat_history"는 대화 메시지를 저장할 키를 지정합니다.
        memory_key="chat_history",
        # output_key="answer"는 메모리에서 출력할 데이터의 키를 설정합니다.
        output_key="answer"
    )