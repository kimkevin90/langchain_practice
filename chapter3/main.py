from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=200,
    # chunk_overlap: chunk_size만큼 문자열 자른 후, 이전 chunk의 지정 값만큼 반영하여 overlap 후 출력
    chunk_overlap=0
)

loader = TextLoader("facts.txt")
docs = loader.load_and_split(
    text_splitter=text_splitter
)

for doc in docs:
    print(doc.page_content)
    print("\n")
