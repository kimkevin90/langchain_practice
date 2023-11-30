# First Time Setup

```
# Create a virtual environment
python -m venv .venv

# On MacOS, WSL, Linux
source .venv/bin/activate

# On Windows
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip3 install --no-cache-dir -r requirements.txt

# Initialize the database
flask --app app.web init-db
```

# Running the app

There are three separate processes that need to be running for the app to work: the server, the worker, and Redis.

If you stop any of these processes, you will need to start them back up!

Commands to start each are listed below. If you need to stop them, select the terminal window the process is running in and press Control-C

### To run the Python server

```
inv dev
```

### To run the worker

```
inv devworker
```

### To run Redis

```
redis-server
```

### To reset the database

```
flask --app app.web init-db
```

# Record
1. create_embeddings_for_pdf 함수 생성 후, pdfLoader 및 chunk filter 적용
2. pinecone.io 벡터스토어사용
3. 메시지 큐를 활용하여 create_embeddings_for_pdf로직을 worker에게 위임
4. 채팅 내역에 관한 기록을 Database에 기록하고 이를 체인에 제공한다.
 - 이전 채팅 내역에 대한 기록을 해야지 전체적인 context 유지 가능
 - 이때, 메모리나, 프론트에서 기록 시, 데이터 휘발 가능성 존재

5. retrieval 사용시 ConversationalRetrieval Chain 사용
 - 모호한 질문에 대해 이전 대화 내역 및 답변을 참고하여 retriever 적용
 - 구성요소:
 Condese Question Chain
 Combine Docs Chain 
 - 위 두체인은 단일 메모리 지원
 - Flow :
 맨처음 질문 시, Condese Question Chain 생략 후, Combine Docs Chain으로 바로 이동하고 메모리에 질문과 대답을 기록한다.
 두번째 질문 시, Condese Question Chain에서 메모리에 질문과 대답을 요약하여 Combine Docs Chain으로 전달하고 Combine Docs Chain은 retriever을 통해 대답한다.
 - 코드 구현
 build_chat 함수 생성하여 chat 관련 내역을 받아 build_retriever함수로 벡터 스토어에서 필터링 후retriever 생성

6. SqlMessageHistory
 - 채팅 내역에 대한 지속성 유지를 위해 Memory 생성
 - ChatMessageHistory기능과 유사하게 메시지를 받아 DB에 저장한 다음 요청이 있을 때마다 해당 목록을 반환
 - conversation_id로 대화 내역 조회
 - 사용자 대화 요청 시, ConverationBufferMemory는 SqlMessageHistory통해 대화 내역 참조