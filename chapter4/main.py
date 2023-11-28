from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from tools.sql import run_query_tool

load_dotenv()

chat = ChatOpenAI()
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template("{input}"),
        # agent_scratchpad: 대화 중에 에이전트가 중간 계산이나 메모, 임시 정보를 저장하는 공간을 의미합니다. 이는 대화 중에 에이전트가 수행한 작업의 중간 결과나 관련 정보를 저장하고 참조하기 위해 사용됩니다.
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

tools=[run_query_tool]

# OpenAIFunctionsAgent는 OpenAI의 언어 모델을 기반으로 하는 에이전트로, 입력된 텍스트를 처리하고, 다양한 도구(tools)를 활용하여 작업을 수행할 수 있습니다.
agent = OpenAIFunctionsAgent(
    llm=chat,
    prompt=prompt,
    tools=tools
)

# AgentExecutor는 OpenAIFunctionsAgent를 실행하고, 사용자의 요청에 대한 처리를 관리하는 역할을 합니다.
agent_executor = AgentExecutor(
    agent=agent,
    verbose=True,
    tools=tools
)

# agent_executor("How many users are in the databases?")
agent_executor("How many users have provided a shipping address?")