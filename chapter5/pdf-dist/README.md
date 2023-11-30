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

7. ConversationalRetrievalChain
 - LLM, Retriever, Memory로 체인을 생성하여 5,6항목을 결합한다.
 - build_llm으로 ChatOpenAi LLM 생성
 - build_chat에서 ConversationalRetrievalChain 생성 후 retriever, llm, memory 적용

8. Testing Streaming Chain
 - 섹션 10
 - 스트리밍을 활용하여 chunk 단위로 response 진행
 - streaming=True 옵션
    -> openAiServer에서는 chunk단위로 결과를 streaming한다. 하지만 LLMChain은 일반 응답일 경우 모든
    응답이 올때까지 리턴하지 않는다.
  - 코드 구현:
    StreamingHandler 생성
    -> openApi 요청 시, 스트리밍 토큰을 얻고 queue에 저장한다.
    StreamingChain 생성
    -> stream 메소드를 오버라이드하고, 스트리밍 문자열을 생성한다.
    -> chain이 실행되는 과정(self(input))은 다른스레드에서 실행시키고 queue에 오는 token을 처리한다.
    -> 스트리밍 데이터를 on_llm_new_token에서 얻을 수 있어야한다. -> Queue로 해결