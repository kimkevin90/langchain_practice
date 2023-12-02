from langchain.callbacks.base import BaseCallbackHandler

class StreamingHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue
        self.streaming_run_ids = set()

    def on_chat_model_start(self, serialized, messages, run_id, **kwargs):
        # serialized : 처음 condense_question_chain은 kwargs프로펄티에 streaming=False로 온다
        print('on_chat_model_start serialized : ',serialized)
        # 고유 식별자
        print('on_chat_model_start run_id : ',run_id)
        # Combine Docs Chain true일 시, 즉 클라이언트에서 스트리밍 모드를 키면 chat_args에 stremaing_True할당
        # on_llm_new_token, on_llm_end, on_llm_error는 stremaing_True시 진행된다.
        if serialized["kwargs"]["streaming"]:
            self.streaming_run_ids.add(run_id)

    def on_llm_new_token(self, token,run_id, **kwargs):
        print('on_llm_new_token : ', run_id)
        self.queue.put(token)

    def on_llm_end(self, response, run_id, **kwargs):
        print('on_llm_end : ', run_id)
        if run_id in self.streaming_run_ids:
            self.queue.put(None)
            self.streaming_run_ids.remove(run_id)

    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)