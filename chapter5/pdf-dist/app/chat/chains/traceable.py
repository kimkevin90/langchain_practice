from langfuse.model import CreateTrace
from app.chat.tracing.langfuse import langfuse

class TraceableChain:
    # StreamingConversationalRetrievalChain를 통해 metadata=chat_args.metadata를 전달 받은 후
    def __call__(self, *args, **kwargs):
        trace = langfuse.trace(
            CreateTrace(
                id=self.metadata["conversation_id"],
                metadata=self.metadata
            )
        )

        # 콜백 조회 후, append 진행하고 키워드에 할당
        callbacks = kwargs.get("callbacks", [])
        callbacks.append(trace.getNewHandler())
        kwargs["callbacks"] = callbacks
        
        return super().__call__(*args, **kwargs)