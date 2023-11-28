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

from tools.sql import run_query_tool, list_tables, describe_tables_tool
from tools.report import write_report_tool 
from handlers.chat_model_start_handler import ChatModelStartHandler

# import langchain
# langchain.debug = True

load_dotenv()

handler = ChatModelStartHandler()
tables = list_tables()
# print(tables)
chat = ChatOpenAI(
    callbacks=[handler]
)
prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=(
            "You are an AI that has access to a SQLite database.\n"
            f"The database has tables of: {tables}\n"
            "Do not make any assumptions about what tables exist "
            "or what columns exist. Instead, use the 'describe_tables' function"
        )),
        # chat_history 키에 기록된 메모리 정보 참조
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        # agent_scratchpad: 대화 중에 에이전트가 중간 계산이나 메모, 임시 정보를 저장하는 공간을 의미합니다. 이는 대화 중에 에이전트가 수행한 작업의 중간 결과나 관련 정보를 저장하고 참조하기 위해 사용됩니다.
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

# 채팅기록 메시지와, 리턴된 메시지의 다른 키워드 인수도 추가
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
tools = [
    run_query_tool,
    describe_tables_tool,
    # write_report_tool
]

# OpenAIFunctionsAgent는 OpenAI의 언어 모델을 기반으로 하는 에이전트로, 입력된 텍스트를 처리하고, 다양한 도구(tools)를 활용하여 작업을 수행할 수 있습니다.
agent = OpenAIFunctionsAgent(
    llm=chat,
    prompt=prompt,
    tools=tools
)

# AgentExecutor는 OpenAIFunctionsAgent를 실행하고, 사용자의 요청에 대한 처리를 관리하는 역할을 합니다.
agent_executor = AgentExecutor(
    agent=agent,
    # verbose=True,
    tools=tools,
    memory=memory
)

agent_executor("How many users are in the databases?")
# agent_executor("Summarize the top 5 most popular products. Write the results to a report file.")

# agent_executor(
#     "How many orders are there? Write the result to an html report."
# )

# agent_executor(
#     "Repeat the exact same process for users."
# )
