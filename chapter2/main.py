from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import MessagesPlaceholder, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.memory import ConversationSummaryMemory, FileChatMessageHistory, ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

chat = ChatOpenAI()

# memory_key='messages': 이 파라미터는 메모리 시스템에서 대화 내용을 저장하거나 접근할 때 사용되는 키(key)를 지정합니다. 여기서 'messages'는 대화의 텍스트 내용을 저장하고 참조하는 데 사용되는 키입니다. 즉, 이 키를 통해 대화 내용에 접근하거나 수정할 수 있습니다.
# return_messages=True: 이 설정은 메모리 시스템이 작동할 때 대화 내용을 반환할지 여부를 결정합니다. return_messages=True로 설정하면, 메모리 시스템이 대화 내용을 반환하며, 이를 통해 대화에 적절하게 응답하거나 필요한 정보를 추출하는 데 사용할 수 있습니다.
memory = ConversationBufferMemory(memory_key='messages', return_messages=True)

prompt = ChatPromptTemplate(
    input_variables=["content", "messages"],
    messages=[
        # ConversationBufferMemory에서 정의된 메모리 키와 연관되어 있습니다. ConversationBufferMemory에서 memory_key='messages'로 설정된 경우, 이 메모리 시스템은 대화의 내용을 'messages'라는 키 아래 저장합니다. MessagesPlaceholder에서 variable_name="messages"를 사용함으로써, 
        # 이 클래스는 'messages' 키 아래 저장된 대화 내용을 참조하여 현재 프롬프트에 적용할 수 있습니다.
        MessagesPlaceholder(variable_name="messages"),
        HumanMessagePromptTemplate.from_template("{content}")
    ]
)

chain = LLMChain(
    llm=chat,
    prompt=prompt,
    memory=memory,
)

while True:
    content = input(">> ")
    
    result = chain({"content": content})

    print(result["text"])
