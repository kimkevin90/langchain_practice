## Deep Dive into Interactions with Memory Management

- pip install langchain openai
- pip install python-dotenv

### 1. ConversationBufferMemory

- ConversationBufferMemory(memory_key='messages', return_messages=True)는 대화 중의 메시지들을 'messages'라는 키로 저장하고 관리하며, 필요한 경우 이 메시지들을 반환하여 대화에 활용할 수 있도록 하는 기능을 제공합니다. 이를 통해 인공지능은 이전 대화의 내용을 참조하면서 사용자와 더욱 연속적이고 의미 있는 대화를 이어갈 수 있습니다.
