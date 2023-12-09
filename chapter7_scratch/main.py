import os
import requests
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langfuse.client import Langfuse
from langfuse.model import CreateTrace
from langfuse.callback import CallbackHandler
from langchain.schema.runnable import RunnablePassthrough
load_dotenv()

handler = CallbackHandler(
    public_key = os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key = os.environ["LANGFUSE_SECRET_KEY"],
    host="https://us.cloud.langfuse.com"
)

SUMMARY_TEMPLATE = """{text} 
-----------
Using the above text, answer in short the following question: 
> {question}
-----------
if the question cannot be answered using the text, imply summarize the text. Include all factual information, numbers, stats etc if available."""

SUMMARY_PROMPT = ChatPromptTemplate.from_template(SUMMARY_TEMPLATE)

def scrape_text(url: str):
    # Send a GET request to the webpage
    try:
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content of the request with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract all text from the webpage
            page_text = soup.get_text(separator=" ", strip=True)

            # Print the extracted text
            return page_text
        else:
            return f"Failed to retrieve the webpage: Status code {response.status_code}"
    except Exception as e:
        print(e)
        return f"Failed to retrieve the webpage: {e}"

url = "https://blog.langchain.dev/announcing-langsmith/"

page_content = scrape_text(url)[:10000]
# print("page_content  :",page_content)

chain = SUMMARY_PROMPT | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser()
result = chain.invoke(
    {
        "question": "What is langsmith",
        "text": page_content
    },
    config={"callbacks": [handler]}
)
handler.langfuse.flush()
print(result)