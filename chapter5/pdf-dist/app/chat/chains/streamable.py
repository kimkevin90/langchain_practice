from flask import current_app
from queue import Queue
from threading import Thread
from app.chat.callbacks.stream import StreamingHandler

class StreamableChain:
    def stream(self, input):
        queue = Queue()
        handler = StreamingHandler(queue)

        def task(app_context):
            app_context.push()
            # 체인에 콜백 핸들러가 연결됐으므로 핸들러의 트리거는 chain과 결합된 모든곳에 영향을 끼침
            self(input, callbacks=[handler])

        # 새 스레드의 앱 컨텍스를 전달
        Thread(target=task, args=[current_app.app_context()]).start()
        
        while True:
            token = queue.get()
            if token is None:
                break
            yield token