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
    "k": 5
}

retriever = vector_store.as_retriever(
    search_kwargs=search_kwargs
)

WRITER_SYSTEM_PROMPT = "You are an AI critical thinker quiz questioner. Your sole purpose is to write well written, critically acclaimed, objective and structured questions on given text."  # noqa: E501

# Report prompts from https://github.com/assafelovic/gpt-researcher/blob/master/gpt_researcher/master/prompts.py
RESEARCH_REPORT_PROMPT = """Information:
--------
{research_summary}
-------- \
Using the above information, answer the detailed questions -- \
should be well structured, informative, in depth, with facts and numbers \
if available and a minimum of 5 questions \
You should strive to write the questions as long as you can using all relevant and necessary information provided.
You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless questions.
Please do your best, this is very important to my career.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", WRITER_SYSTEM_PROMPT),
        ("user", RESEARCH_REPORT_PROMPT),
    ]
)




def format_docs(docs):
    print("docs : ", docs)
    return "\n\n".join([d.page_content for d in docs])

chain = (
    {"research_summary": retriever | format_docs}
    | prompt
    # | ChatOpenAI(model="gpt-3.5-turbo-1106")
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)
result = chain.invoke(
    "Summarize the information provided",
    config={"callbacks": [handler]})
handler.langfuse.flush()
print(result)