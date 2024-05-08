import os
import requests
import json
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langfuse.client import Langfuse
from langfuse.model import CreateTrace
from langfuse.callback import CallbackHandler
from langchain.schema.runnable import RunnablePassthrough,RunnableParallel
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter

load_dotenv()

'''
- Prompt 3: Skeleton Prompt Template Ts (with Two-Shot Demonstrations)
[User:] You’re an organizer responsible for only giving the skeleton (not the full content) for answering the question. Provide the skeleton in a list of points (numbered 1., 2., 3., etc.) to answer the question. Instead of writing a full sentence, each skeleton point should be very short with only 3∼5 words. Generally, the skeleton should have 3∼10 points.
Question:
What are the typical types of Chinese dishes? Skeleton:
1. Dumplings.
2. Noodles.
3. Dim Sum.
4. Hot Pot.
5. Wonton.
6. Ma Po Tofu.
7. Char Siu.
8. Fried Rice.
Question:
What are some practical tips for individuals to reduce their carbon emissions? Skeleton:
1. Energy conservation.
2. Efficient transportation.
3. Home energy efficiency.
4. Reduce water consumption.
5. Sustainable diet.
6. Sustainable travel.
Now, please provide the skeleton for the following question.
{question} Skeleton: [Assistant:] 1.

프롬프트 3: 스켈레톤 프롬프트 템플릿 Ts(투샷 데모 포함): 이 프롬프트는 SoT 방법의 스켈레톤 단계에서 사용됩니다. 
이 방법은 인간이 체계적인 방식으로 생각하고 질문에 답한다는 생각에 기반합니다. 
따라서 전체 답변을 작성하기 전에 먼저 답변의 간결한 골격을 만들도록 LLM을 안내합니다. 
프롬프트 3에서 볼 수 있는 스켈레톤 프롬프트 템플릿(Ts)은 이 간결한 스켈레톤을 출력하도록 LLM에 지시하기 위해 만들어졌습니다. 
이 접근 방식을 사용하면 체계적이고 간결한 답변을 생성할 수 있으므로 자세한 설명으로 들어가기 전에 명확하고 간략한 개요가 필요한 시나리오에서 특히 유용할 수 있습니다.

권장 사용법: 이 프롬프트는 복잡한 주제나 여러 부분으로 구성된 질문에 대한 구조적이고 간결한 개요가 필요할 때 가장 적합합니다. 
세부 사항을 자세히 설명하기 전에 요점을 파악하고 명확하게 정리해야 하는 상황에서 특히 유용합니다.

예시 상황: "기후 변화가 세계 농업에 미치는 영향"과 같은 복잡한 주제를 이해하기 위해 대규모 언어 모델(LLM)을 사용한다고 상상해 보세요. 
긴 설명으로 바로 뛰어드는 대신 프롬프트 3을 사용하여 먼저 골격 답변을 생성할 수 있습니다. 이 골격에는 "농작물 수확량 변화", "농업 지대의 변화", 
"농업 공동체에 대한 경제적 영향", "완화 전략" 등의 핵심 사항이 포함될 수 있습니다. 그런 다음 이러한 각 요점을 전체 답변에서 확장하여 체계적이고 포괄적인 답변을 제공할 수 있습니다.

- Prompt 4: LLM Prompting as the Router
User:] Question: {question}
How would you like to answer the question?
A. Organize the answer as a list of points or perspectives (in the format of 1., 2., 3., etc.), and the points or perspectives can be answered independently without referring to the contents of the previous points.
B. Organize the answer as a list of points or perspectives (in the format of 1., 2., 3., etc.), and the contents of later points or perspectives cannot be answered independently without referring to the contents of the previous ones.
C. Do not organize the answer as a list of points or perspectives.
Just say A, B, or C. Do not explain. Do not provide an answer to the question.
[Assistant:]

프롬프트 4: 라우터로 LLM 프롬프트: 이 프롬프트는 다자간 대화에서 SoT를 사용할 때 사용됩니다. 
이 프롬프트는 주어진 질문에 SoT를 사용할지 여부를 결정하는 '라우터' 역할을 합니다. 
라우터는 질문이 독립적인 포인트 목록(사례 "A")으로 답할 수 있는지 평가하며, 이 경우 SoT가 사용됩니다. 
답변이 상호 의존적인 점의 목록으로 더 적합하거나(사례 "B") 목록 형식이 아니어야 하는 경우(사례 "C") SoT가 부적합한 것으로 간주되어 일반 디코딩이 대신 사용됩니다. 
이 프롬프트는 SoT가 가장 효과적인 질문에만 적용되도록 함으로써 다양한 유형의 쿼리에 대한 응답 생성 프로세스를 최적화합니다.

권장 사용법: 이 프롬프트는 여러 차례에 걸친 대화 또는 각 질문에 가장 효과적인 답변 방법을 결정해야 하는 일련의 질문을 처리할 때 이상적입니다. 
이 프롬프트는 의사 결정 도구의 역할을 하며, 구조화된 요점 중심 접근 방식(SoT)을 사용할지 아니면 보다 전통적인 흐름형 내러티브를 사용할지 안내합니다.

상황 예시: "인공지능(AI)의 발전과 그 윤리적 함의"에 대해 법학석사 학위 취득자와 주고받는 토론을 하는 시나리오를 생각해 보세요. 
대화의 각 질문마다 다른 접근 방식이 필요할 수 있습니다. 예를 들어, "AI 개발의 주요 이정표를 나열하세요"와 같은 질문은 뚜렷하고 독립적인 요점을 요구하므로 
SoT를 사용하여 답변하는 것이 가장 적합할 수 있습니다. 그러나 "이러한 발전이 윤리적 문제를 어떻게 제기하나요?"와 같은 후속 질문은 개념에 대한 상호 연결된 설명이 필요하므로 목록 형식에 적합하지 않을 수 있습니다. 
여기서 프롬프트 4는 언제 SoT를 사용할지, 언제 일반 응답 형식을 선택할지 결정하여 각 질문에 가장 적절하고 효과적인 방식으로 답변할 수 있도록 도와줍니다.

요약하면, 두 프롬프트 모두 LLM 응답의 품질과 구조를 개선하는 것을 목표로 하지만, 그 목적은 서로 다릅니다: 
프롬프트 3은 답변의 체계적인 골격을 만들기 위한 것으로 복잡하고 다면적인 질문에 유용한 반면, 
프롬프트 4는 대화에서 라우팅 메커니즘의 역할을 하여 각 쿼리에 가장 적합한 답변 형식을 평가합니다.
'''

embeddings = OpenAIEmbeddings()

handler = CallbackHandler(
    public_key = os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key = os.environ["LANGFUSE_SECRET_KEY"],
    host="https://us.cloud.langfuse.com"
)
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV_NAME")
)
vector_store = Pinecone.from_existing_index(
    os.getenv("PINECONE_INDEX_NAME"), embeddings
)
search_kwargs = {
    "filter": { "pdf_id": "568f04ce-49e0-4c70-ad0d-92deb169d761" },
    "k": 3
}

retriever = vector_store.as_retriever(
    search_kwargs=search_kwargs
)
# print('retriever : ',retriever)

skeleton_generator_template = """Information:
--------
{context}
-------- \
[User:] You’re an organizer responsible for only \
giving the skeleton (not the full content) for answering the question.
Using the above information, Provide the skeleton in a list of points (numbered 1., 2., 3., etc.) to answer \
the question. \
Instead of writing a full sentence, each skeleton point should be very short \
with only 3∼5 words. \
Generally, the skeleton should have 3∼10 points. Now, please provide the skeleton \
for the following question.
{question}
Skeleton:
[Assistant:] 1."""

# skeleton_generator_template = """Answer the question based only on the following context:

# {context}

# Question: {question}
# """

skeleton_generator_prompt = ChatPromptTemplate.from_template(
    skeleton_generator_template
)



def format_docs(docs):
    # print("docs : ", docs)
    return "\n\n".join([d.page_content for d in docs])

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | skeleton_generator_prompt
    # | ChatOpenAI(model="gpt-3.5-turbo-1106")
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)

input_schema = chain.input_schema.schema()
print(input_schema)
result = chain.invoke("Which country sold the most spices?", config={"callbacks": [handler]})
handler.langfuse.flush()
# print(result)