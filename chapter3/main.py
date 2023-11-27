from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings()

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

# Chroma.from_documents 메서드는 주어진 문서들(docs)과 해당 문서들의 임베딩(embeddings)을 사용하여 벡터 저장소(db)를 생성합니다.
# persist_directory="emb"는 생성된 벡터 저장소를 지정된 디렉토리("emb")에 지속적으로 저장하겠다는 의미입니다. 
# 이렇게 함으로써, 나중에 시스템을 재시작하거나 다른 작업을 수행할 때 저장소를 다시 로드할 수 있습니다.
db = Chroma.from_documents(
    docs,
    embedding=embeddings,
    persist_directory="emb"
)

results = db.similarity_search(
    "What is an interesting fact about the English language?"
)

for result in results:
    print("\n")
    print(result.page_content)
