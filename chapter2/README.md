# LangChain 대화 메모리 시스템

이 문서에서는 LangChain에서 사용되는 두 가지 대화 메모리 시스템, `ConversationBufferMemory`와 `ConversationSummaryMemory`의 차이점과 각각의 특징에 대해 설명합니다.

## `ConversationBufferMemory`

### 설명
- `ConversationBufferMemory`는 대화의 모든 메시지를 순서대로 저장하고 관리하는 메모리 시스템입니다.
- 대화 중 발생한 모든 텍스트 내용이 이 시스템에 저장됩니다.

### 예시
```python
memory = ConversationBufferMemory(memory_key='messages', return_messages=True)
```
