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
 1) 섹션 10 test.py 테스트
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
  
  2) 섹션11 test.py 리팩토링
  - 기존 queue는 모든 요청에 하나의 queue를 사용하므로, 여러사용자의 요청시 문제발생
  - 체인 실행 시, queue와 handler를 생성하도록 StreamingChain의 stream 메소드를 변경한다.
  - 확장성 고려하여, StreamableChain 생성 후, 필요에 따른 Chain적용하도록 변경

  3) 섹션11 실제 코드 적용
  - build_chat의 ConversationalRetrievalChain을 StreamingConversationalRetrievalChain로 변경
  -> 스트리밍을 위해 기존의 ConversationalRetrievalChain과 StreamableChain을 연결
  - build_llm에 streaming 옵션 추가
  - flask는 새로운 스레드를 사용하면 앱context 정보에 엑세스할 수 없다. 따라서, current_app.app_context()로 앱context를 전달한다.
  4) 섹션 11_스트리밍 시, Condese Question Chain 오작동 문제 발생한다.
  -> 스트리밍 시, Condese Question Chain은 일부 토큰을 방출하기 시작하고, 그런 다음 결국 응답을 완료하게 되며, 이 시점에서 스트리밍 핸들러는 해당 대기열을 닫고 더 이상 토큰을 받을 것으로 예상하지 않는다고 말합니다. 따라서 압축된 질문 체인을 마치자마자 스트리밍 핸들러는 기본적으로 나머지 내용을 알려줍니다.(사진 streamproblem.png)
  -> 결국 문제는 Condese Question Chain과 Combine Docs Chain이 동일한 LLM과 StreamingHandler를 사용해서 발생하는 것이다. 즉, StreamingHandler의 트리거 이벤트가 두 체인에서 모두 일어나기 때문이다.
  - 해결책 :
  Condese Question Chain에는 streaming=False로, Combine Docs Chain은 streaming=True로 하여 핸들러를 필요로 하는곳에서만 이벤트를 발생시킨다.(사진 streaming_sol.png)
  구현 :
  1) StreamingConversationalRetrievalChain.from_llm는 인자로 condense_question_llm를 받으므로 새로운 llm을 이에 할당한 후 streaming=False를 전달한다.
  2) StreamingHandler serialized의 kwargs의 streaming=True일 경우 핸들러 이벤트를 적용한다.

9. 섹션 12_Self-Improving Text Generation 
 - 문제점 : 선택한 gpt3.5, pinecone의 조합이 완벽하지 않을 수 있다. 따라서, 무작의로 llm, memory, retriever를 조합하고 클라이언트에서 좋아요 등으로 평가할 수 있도록하여 최적의 조합을 찾을 수 있도록 한다.
 - 구현방법 
  1) ComponentMaps를 생성하여, retrievers, memory, llm에 여러 솔루션들을 담는다. (사진 componentmap.png)
  2) 클라이언트에서 채팅 시, ComponentMaps를에서 무작위로 retriever, memory, llm을 선택하여 RetrievalChain을 생성한다.
  3) DB에 무작위로 선택한 retriever, memory, llm을 기록하고, 응답을 보낸다.
  4) 클라이언트에서 두번째, 세번째 계속하여 요청보내면 무작위 선택 작업을 하지 않고, DB에 기록된 세팅으로 응답을 보낸다.
  - 코드구현
  1) build_llm에 model_name인수를 생성하고, llm_map으로 gpt4, gpt3.5를 인수를 자동 전달할 수 있도록 구성한다.
  2) build_retriever로 k 인수 설정 및 retriever_map 생성
  3) memory_map 생성
  4) build_chat 수정 : get_conversation_components, set_conversation_components 사용하여, 저장된 componentMap 설정 사용하도록 변경
  5) 각 메시지별 평점 적용 (사진, scoreflow.png)
  - Redis에 LLM, Retriever, Memory Score 자료구조를 통해 평균값을 저장
  -> 이때 Redis는 평균 계산을 지원하지 않기 때문에 각 항목에 대한 Total과, Count 자료구조를 생성하여 Total 점수 / Count로 평균 적용 (사진, scoreRedisStructure.png)
  코드 구현 :
  -> 새로운 대화 시작 시 random_component_by_score를 통해 평균 및 가중치를 통해 llm, retriever, memory를 반환
  -> score_conversation를 통해 llm, retriever, memory에 대한 total, count 증가
  -> get_scores를 통해 현재 평가된 llm, retriever, memory에대한 평균 스코어를 반환

10. 섹션13_Implementing Tracing and Observability
  1) ConversationBufferWindowMemory 적용 : ConversationBufferWindowMemory는 ConversationBufferMemory의 변형으로, 대화 중 생성된 정보를 저장하지만, 일정 범위(window) 내의 메시지만 유지합니다.
  주요 특징
  윈도우 기반 저장: 대화의 특정 범위(예: 최근 N개의 메시지)만을 저장합니다. 이를 통해 메모리 사용량을 제한하고, 가장 관련성 높은 대화 내용에 집중할 수 있습니다.
  메모리 효율성: 전체 대화 기록 대신 일부만 저장함으로써 메모리 사용량을 최적화합니다.
  최신 대화에 집중: 에이전트가 최근의 대화 내용에 더 집중하여 응답할 수 있도록 돕습니다. 이는 특히 대화가 길어질 때 유용합니다.
  2) LangFuse사용
  - 텍스트 생성 프로세스에 대한 데이터를 수집하여 웹사이트에 표시