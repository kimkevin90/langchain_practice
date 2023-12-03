from pydantic import BaseModel
from langchain.schema import BaseChatMessageHistory

from app.web.api import (
    get_messages_by_conversation_id,
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