from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv
from queue import Queue
from threading import Thread


load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue  = queue

    def on_llm_new_token(self, token, **kwargs):
        # 각 chunk 텍스트를 Queue에 저장
        self.queue.put(token)

    # 언어 모델이 응답을 완료했을 때 호출됩니다.
    # 스트리밍 작업의 종료를 알리기 위해 self.queue에 None을 추가합니다.
    def on_llm_end(self, response, **kwargs):
        self.queue.put(None)

    # 언어 모델 처리 중 오류가 발생했을 때 호출됩니다.
    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)
'''
실시간 토큰 생성: 언어 모델이 응답을 생성하는 동안, 생성되는 각 토큰(token)을 실시간으로 반환합니다. 
즉, 전체 응답이 완성되기 전에도 응답의 일부를 계속해서 받을 수 있습니다.
스트리밍 모드의 콜백 처리: 스트리밍 모드에서는 StreamingHandler와 같은 콜백 핸들러가 활용됩니다. 
이 핸들러는 모델이 새 토큰을 생성할 때마다, 대화가 종료되었을 때, 또는 오류가 발생했을 때 호출되어 특정 작업을 수행합니다.
'''
chat = ChatOpenAI(
    # streaming=True: OpenAI to stream to LangChain
    streaming=True,
    # # 스트리밍 핸들러 적용 -> StreamingChain의 stream 메소드로 이동
    # callbacks=[StreamingHandler()]
)

prompt = ChatPromptTemplate.from_messages([
    ("human", "{content}")
])

class StreamableChain:
    # stream 메소드는 별도의 스레드에서 실행됩니다. 이를 통해 메인 프로그램의 실행을 차단하지 않고, 대화 처리를 비동기적으로 수행할 수 있습니다.
    def stream(self, input):
        queue = Queue()
        handler = StreamingHandler(queue)
        # 체인을 실행시키는 메소드
        def task():
            # print('self(input) : ',self(input))
            # 체인 실행할때 콜백함수에 handler적용
            self(input, callbacks=[handler])

        # 다른 스레드에서 chain을 실행하므로 바로 while문으로 넘어가게된다.
        Thread(target=task).start()
        
        # 제너레이터에서 token이 있을 경우 yield를 통해 토큰을 반환한다.
        # 다른 스레드에서 queue에 토큰을 넣어주고, None이 있을 경우 끝났으므로 break 진행
        while True:
            token = queue.get()
            if token is None:
                break
            yield token

# 추후에 LLMChain말고 conversationChain등도 가능하도록 한다.
class StreamingChain(StreamableChain, LLMChain):
    pass

chain = StreamingChain(llm=chat, prompt=prompt)

'''
StreamableChain 클래스는 LLMChain을 확장하여 스트리밍 대화 기능을 추가합니다. stream 메소드는 다음과 같이 작동합니다:
비동기적 대화 처리: stream 메소드는 별도의 스레드에서 ChatOpenAI 모델을 사용하여 입력을 처리합니다. 
이렇게 하면 메인 프로그램의 흐름을 차단하지 않고 대화를 진행할 수 있습니다.
실시간 토큰 스트리밍: ChatOpenAI에서 생성되는 토큰들은 queue를 통해 stream 메소드에 전달됩니다. 
stream 메소드는 이 토큰들을 실시간으로 yield를 통해 반환하며, 사용자는 이를 순차적으로 받아볼 수 있습니다.
'''
# stream : stream's forces streaming everywhere regardless of the treaming flag
# streaming=False로 해도 stream 처리한다.
# 일반 chian 클래스의 stream 메소드는 chunk단위로 결과를 주지않으므로, StreamingChain를 사용하여 stream 메소드 오버라이드하여 적용한다.
for output in chain.stream(input={"content": "tell me a joke"}):
    print(output)