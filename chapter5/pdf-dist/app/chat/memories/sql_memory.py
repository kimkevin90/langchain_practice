from pydantic import BaseModel
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseChatMessageHistory

from app.web.api import (
    # 유저A와의 채팅 내역 id
    get_messages_by_conversation_id,
    # 대화내역 db에 추가
    add_message_to_conversation
)

# SqlMessageHistory 클래스는 BaseChatMessageHistory를 확장하고 
# BaseModel을 상속하여 Pydantic 모델로 정의됩니다. 
# 이 클래스는 대화 내용을 SQL 데이터베이스에 저장하고 관리하는 역할을 합니다.
class SqlMessageHistory(BaseChatMessageHistory, BaseModel):
    conversation_id: str

    @property
    def messages(self):
        return get_messages_by_conversation_id(self.conversation_id)
    
    def add_message(self, message):
        return add_message_to_conversation(
            conversation_id=self.conversation_id,
            role=message.type,
            content=message.content
        )

    def clear(self):
        pass

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