from operator import itemgetter
import os
import math
import time
import asyncio
import pinecone
import json
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.vectorstores.pinecone import Pinecone
from langfuse.callback import CallbackHandler
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableConfig,RunnableBranch,ConfigurableField
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatAnthropic
# from langchain.runnables.hub import HubRunnable


from dotenv import load_dotenv
load_dotenv()

handler = CallbackHandler(
    public_key = os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key = os.environ["LANGFUSE_SECRET_KEY"],
    host="https://us.cloud.langfuse.com"
)

# start = time.time()
# math.factorial(100000)
# end = time.time()

# handler = CallbackHandler(
#     public_key = os.environ["LANGFUSE_PUBLIC_KEY"],
#     secret_key = os.environ["LANGFUSE_SECRET_KEY"],
#     host="https://us.cloud.langfuse.com"
# )

# embeddings = OpenAIEmbeddings()
# pinecone.init(
#     api_key=os.getenv("PINECONE_API_KEY"),
#     environment=os.getenv("PINECONE_ENV_NAME")
# )
# vector_store = Pinecone.from_existing_index(
#     os.getenv("PINECONE_INDEX_NAME"), embeddings
# )
# search_kwargs = {
#     "filter": { "pdf_id": "568f04ce-49e0-4c70-ad0d-92deb169d761" },
#     "k": 1
# }

# retriever = vector_store.as_retriever(
#     search_kwargs=search_kwargs
# )
# template = """Answer the question based only on the following context:
# {context}

# Question: {question}
# """
# prompt = ChatPromptTemplate.from_template(template)
# model = ChatOpenAI()

# retrieval_chain = (
#     {"context": retriever, "question": RunnablePassthrough()}
#     | prompt
#     | model
#     | StrOutputParser()
# )

# result = retrieval_chain.invoke("Which country sold the most spices?",config={"callbacks": [handler]})
# handler.langfuse.flush()
# print(result)



'''
Using itemgetter as shorthand
'''




# embeddings = OpenAIEmbeddings()
# pinecone.init(
#     api_key=os.getenv("PINECONE_API_KEY"),
#     environment=os.getenv("PINECONE_ENV_NAME")
# )
# vector_store = Pinecone.from_existing_index(
#     os.getenv("PINECONE_INDEX_NAME"), embeddings
# )
# search_kwargs = {
#     "filter": { "pdf_id": "568f04ce-49e0-4c70-ad0d-92deb169d761" },
#     "k": 1
# }

# retriever = vector_store.as_retriever(
#     search_kwargs=search_kwargs
# )

# model = ChatOpenAI()
# template = """Answer the question based only on the following context:
# {context}

# Question: {question}

# Answer in the following language: {language}
# """
# prompt = ChatPromptTemplate.from_template(template)

# chain = (
#     {
#         "context": itemgetter("question") | retriever,
#         "question": itemgetter("question"),
#         "language": itemgetter("language"),
#     }
#     | prompt
#     | model
#     | StrOutputParser()
# )

# result = chain.invoke({
#     "question": "Which country sold the most spices?", 
#     "language": "korean"
#     },
# config={"callbacks": [handler]})

# handler.langfuse.flush()
# print(result)


'''
Parallelize steps
'''

# model = ChatOpenAI()
# joke_chain = ChatPromptTemplate.from_template("tell me a joke about {topic}") | model
# poem_chain = (
#     ChatPromptTemplate.from_template("write a 2-line poem about {topic}") | model
# )

# map_chain = RunnableParallel(joke=joke_chain, poem=poem_chain)

# map_chain.invoke({"topic": "bear"}, config={"callbacks": [handler]})

'''
Passing data through

- RunnablePassthrough는 입력을 변경하지 않거나 추가 키를 추가하여 전달할 수 있습니다. 일반적으로 맵의 새 키에 데이터를 할당하기 위해 RunnableParallel과 함께 사용됩니다.
단독으로 호출되는 RunnablePassthrough()는 단순히 입력을 받아 통과시킵니다.
assign과 함께 호출(RunnablePassthrough.assign(...))하면 입력을 받고, 할당 함수에 전달된 추가 인수를 추가합니다.
'''

# from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# runnable = RunnableParallel(
#     passed=RunnablePassthrough(),
#     extra=RunnablePassthrough.assign(mult=lambda x: x["num"] * 3),
#     modified=lambda x: x["num"] + 1,
# )

# result = runnable.invoke({"num": 2}, config={"callbacks": [handler]})

'''
Run custom functions

- 파이프라인에서 임의의 함수를 사용할 수 있습니다.
이러한 함수에 대한 모든 입력은 단일 인수여야 한다는 점에 유의하세요. 
여러 개의 인수를 받는 함수가 있는 경우 단일 입력을 받아 여러 개의 인수로 압축을 푸는 래퍼를 작성해야 합니다.
'''

# def length_function(text):
#     return len(text)


# def _multiple_length_function(text1, text2):
#     return len(text1) * len(text2)


# def multiple_length_function(_dict):
#     return _multiple_length_function(_dict["text1"], _dict["text2"])


# prompt = ChatPromptTemplate.from_template("what is {a} + {b}")
# model = ChatOpenAI()

# chain = (
#     {
#         "a": itemgetter("foo") | RunnableLambda(length_function),
#         "b": {"text1": itemgetter("foo"), "text2": itemgetter("bar")}
#         | RunnableLambda(multiple_length_function),
#     }
#     | prompt
#     | model
# )

# # 동일함
# # runnable = RunnableParallel(
# #     a = itemgetter("foo") | RunnableLambda(length_function),
# #     b = {"text1": itemgetter("foo"), "text2": itemgetter("bar")} | RunnableLambda(multiple_length_function)
# # )

# # chain = runnable | prompt | model

# result = chain.invoke({"foo": "bar", "bar": "gah"},config={"callbacks": [handler]})


'''
Accepting a Runnable Config

- Runnable lambdas can optionally accept a RunnableConfig, which they can use to pass callbacks, tags, and other configuration information to nested runs.

'''
# def parse_or_fix(text: str, config: RunnableConfig):
#     fixing_chain = (
#         ChatPromptTemplate.from_template(
#             "Fix the following text:\n\n```text\n{input}\n```\nError: {error}"
#             " Don't narrate, just respond with the fixed data."
#         )
#         | ChatOpenAI()
#         | StrOutputParser()
#     )
#     for _ in range(3):
#         try:
#             return json.loads(text)
#         except Exception as e:
#             text = fixing_chain.invoke({"input": text, "error": e}, config)
#     return "Failed to parse"

# with get_openai_callback() as cb:
#     output = RunnableLambda(parse_or_fix).invoke(
#         "{foo: bar}", {"tags": ["my-tag"], "callbacks": [cb]}, 
#     )
#     print(output)
#     print(cb)


'''
Dynamically route logic based on input

- 이 노트북은 LangChain 표현식 언어에서 라우팅을 수행하는 방법을 다룹니다.
라우팅을 사용하면 이전 단계의 출력이 다음 단계를 정의하는 비결정적 체인을 만들 수 있습니다. 라우팅은 LLM과의 상호 작용에 대한 구조와 일관성을 제공하는 데 도움이 됩니다.
라우팅을 수행하는 방법에는 두 가지가 있습니다:
런처블 브랜치 사용.
이전 단계의 입력을 받아 런처블을 반환하는 사용자 정의 팩토리 함수를 작성합니다. 중요한 것은 런처블을 반환하고 실제로 실행하지 않아야 한다는 것입니다.
여기서는 두 가지 방법 모두 첫 번째 단계에서 입력 질문을 LangChain, Anthropic 또는 기타로 분류한 다음 해당 프롬프트 체인으로 라우팅하는 두 단계 시퀀스를 사용하여 설명하겠습니다.

'''

'''
Using a RunnableBranch - 분기처리

'''

# chain = (
#     ChatPromptTemplate.from_template(
#         """Given the user question below, classify it as either being about `LangChain`, `Anthropic`, or `Other`.

# Do not respond with more than one word.

# <question>
# {question}
# </question>

# Classification:"""
#     )
#     | ChatOpenAI(model="gpt-3.5-turbo-1106")
#     | StrOutputParser()
# )

# langchain_chain = (
#     ChatPromptTemplate.from_template(
#         """You are an expert in langchain. \
# Always answer questions starting with "As Harrison Chase told me". \
# Respond to the following question:

# Question: {question}
# Answer:"""
#     )
#     | ChatOpenAI(model="gpt-3.5-turbo-1106")
# )
# anthropic_chain = (
#     ChatPromptTemplate.from_template(
#         """You are an expert in anthropic. \
# Always answer questions starting with "As Dario Amodei told me". \
# Respond to the following question:

# Question: {question}
# Answer:"""
#     )
#     | ChatOpenAI(model="gpt-3.5-turbo-1106")
# )
# general_chain = (
#     ChatPromptTemplate.from_template(
#         """Respond to the following question:

# Question: {question}
# Answer:"""
#     )
#     | ChatOpenAI(model="gpt-3.5-turbo-1106")
# )

# branch = RunnableBranch(
#     (lambda x: "anthropic" in x["topic"].lower(), anthropic_chain),
#     (lambda x: "langchain" in x["topic"].lower(), langchain_chain),
#     general_chain,
# )

## 아래와 같이 RunnableLambda사용하여 분기처리도 가능함
## def route(info):
##     if "anthropic" in info["topic"].lower():
##         return anthropic_chain
##     elif "langchain" in info["topic"].lower():
##         return langchain_chain
##     else:
##         return general_chain
#
## full_chain = {"topic": chain, "question": lambda x: x["question"]} | RunnableLambda(
##     route
## )


# full_chain = {"topic": chain, "question": lambda x: x["question"]} | branch
# result = full_chain.invoke({"question": "how do I use Anthropic?"}, config={"callbacks": [handler]})

# # result = full_chain.invoke({"question": "whats 2 + 2"}, config={"callbacks": [handler]})


'''
Bind runtime args
- bind()를 사용하여 system 메시지에서 특정 요청을 삭제한다.
Sometimes we want to invoke a Runnable within a Runnable sequence with constant arguments that are not part of the output of the preceding Runnable in the sequence, 
and which are not part of the user input. We can use Runnable.bind() to easily pass these arguments in.

'''

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Write out the following equation using algebraic symbols then solve it. Use the format\n\nEQUATION:...\nSOLUTION:...\n\n",
#         ),
#         ("human", "{equation_statement}"),
#     ]
# )
# model = ChatOpenAI(temperature=0)

# # bind()적용안할 시
# # runnable = (
# #     {"equation_statement": RunnablePassthrough()} | prompt | model | StrOutputParser()
# # )

# runnable = (
#     {"equation_statement": RunnablePassthrough()}
#     | prompt
#     | model.bind(stop="SOLUTION")
#     | StrOutputParser()
# )

# result = runnable.invoke("x raised to the third plus seven equals 12")

'''
Attaching OpenAI functions
One particularly useful application of binding is to attach OpenAI functions to a compatible OpenAI model:
- 바인딩의 특히 유용한 응용 분야 중 하나는 호환되는 OpenAI 모델에 OpenAI 함수를 첨부하는 것입니다
'''

# function = {
#     "name": "solver",
#     "description": "Formulates and solves an equation",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "equation": {
#                 "type": "string",
#                 "description": "The algebraic expression of the equation",
#             },
#             "solution": {
#                 "type": "string",
#                 "description": "The solution to the equation",
#             },
#         },
#         "required": ["equation", "solution"],
#     },
# }

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Write out the following equation using algebraic symbols then solve it.",
#         ),
#         ("human", "{equation_statement}"),
#     ]
# )
# model = ChatOpenAI(model="gpt-4", temperature=0).bind(
#     function_call={"name": "solver"}, functions=[function]
# )
# runnable = {"equation_statement": RunnablePassthrough()} | prompt | model 

# result = runnable.invoke("x raised to the third plus seven equals 12" ,config={"callbacks": [handler]})
# # content='' additional_kwargs={'function_call': {'name': 'solver', 'arguments': '{\n"equation": "x^3 + 7 = 12",\n"solution": "x = ∛5"\n}'}}

'''
Attaching OpenAI tools

'''

# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_current_weather",
#             "description": "Get the current weather in a given location",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "location": {
#                         "type": "string",
#                         "description": "The city and state, e.g. San Francisco, CA",
#                     },
#                     "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#                 },
#                 "required": ["location"],
#             },
#         },
#     }
# ]

# model = ChatOpenAI(model="gpt-3.5-turbo-1106").bind(tools=tools)
# model.invoke("What's the weather in SF, NYC and LA?")

'''
Configure chain internals at runtime
- 여러 가지 다른 작업 방식을 실험하거나 이를 최종 사용자에게 노출하고 싶을 때가 종종 있습니다. 
이러한 경험을 최대한 쉽게 제공하기 위해 두 가지 메서드를 정의했습니다.
첫째, configurable_fields 메서드입니다. 이를 통해 runnable의 특정 필드를 구성할 수 있습니다.
둘째, configurable_alternatives 메서드. 이 메서드를 사용하면 런타임 중에 설정할 수 있는 특정 runnable의에 대한 대안을 나열할 수 있습니다.
'''

# model = ChatOpenAI(temperature=0).configurable_fields(
#     temperature=ConfigurableField(
#         id="llm_temperature",
#         name="LLM Temperature",
#         description="The temperature of the LLM",
#     )
# )

# # temperature 옵션 바꾸기
# # result = model.with_config(configurable={"llm_temperature": 0.9}).invoke("pick a random number", config={"callbacks": [handler]})

# prompt = PromptTemplate.from_template("Pick a random number above {x}")
# chain = prompt | model
# result = chain.with_config(configurable={"llm_temperature": 0.9}).invoke({"x": 0})


'''
With HubRunnables
- This is useful to allow for switching of prompts
'''

# prompt = HubRunnable("rlm/rag-prompt").configurable_fields(
#     owner_repo_commit=ConfigurableField(
#         id="hub_commit",
#         name="Hub Commit",
#         description="The Hub commit to pull from",
#     )
# )

# result = prompt.with_config(configurable={"hub_commit": "rlm/rag-prompt-llama"}).invoke(
#     {"question": "foo", "context": "bar"}
# )


'''
With LLMs
- Let’s take a look at doing this with LLMs
'''

# llm = ChatOpenAI(temperature=0).configurable_alternatives(
#     # This gives this field an id
#     # When configuring the end runnable, we can then use this id to configure this field
#     ConfigurableField(id="llm"),
#     # This adds a new option, with name `openai` that is equal to `ChatOpenAI()`
#     openai=ChatOpenAI(model="gpt-3.5-turbo-1106"),
#     # This adds a new option, with name `gpt4` that is equal to `ChatOpenAI(model="gpt-4")`
#     gpt4=ChatOpenAI(model="gpt-43423"),
#     # You can add more configuration options here
# )
# prompt = PromptTemplate.from_template("Tell me a joke about {topic}")
# chain = prompt | llm

# result = chain.with_config(configurable={"llm": "openai"}).invoke({"topic": "bears"})

'''
With Prompts
- We can do a similar thing, but alternate between prompts
'''

# llm = ChatOpenAI(temperature=0)
# prompt = PromptTemplate.from_template(
#     "Tell me a joke about {topic}"
# ).configurable_alternatives(
#     # This gives this field an id
#     # When configuring the end runnable, we can then use this id to configure this field
#     ConfigurableField(id="prompt"),
#     # This sets a default_key.
#     # If we specify this key, the default LLM (ChatAnthropic initialized above) will be used
#     default_key="joke",
#     # This adds a new option, with name `poem`
#     poem=PromptTemplate.from_template("Write a short poem about {topic}"),
#     # You can add more configuration options here
# )
# chain = prompt | llm

# result = chain.with_config(configurable={"prompt": "poem"}).invoke({"topic": "bears"}, config={"callbacks": [handler]})

'''
With Prompts and LLMs
- We can also have multiple things configurable! Here’s an example doing that with both prompts and LLMs.
'''

# llm = ChatOpenAI(temperature=0).configurable_alternatives(
#     # This gives this field an id
#     # When configuring the end runnable, we can then use this id to configure this field
#     ConfigurableField(id="llm"),
#     # This adds a new option, with name `openai` that is equal to `ChatOpenAI()`
#     openai=ChatOpenAI(model="gpt-3.5-turbo-1106"),
#     # This adds a new option, with name `gpt4` that is equal to `ChatOpenAI(model="gpt-4")`
#     gpt4=ChatOpenAI(model="gpt-43423"),
#     # You can add more configuration options here
# )

# prompt = PromptTemplate.from_template(
#     "Tell me a joke about {topic}"
# ).configurable_alternatives(
#     # This gives this field an id
#     # When configuring the end runnable, we can then use this id to configure this field
#     ConfigurableField(id="prompt"),
#     # This sets a default_key.
#     # If we specify this key, the default LLM (ChatAnthropic initialized above) will be used
#     default_key="joke",
#     # This adds a new option, with name `poem`
#     poem=PromptTemplate.from_template("Write a short poem about {topic}"),
#     # You can add more configuration options here
# )
# chain = prompt | llm


# openai_poem = chain.with_config(configurable={"prompt": "poem", "llm": "openai"})

# result = openai_poem.invoke({"topic": "bears"})


print(result)
handler.langfuse.flush()

