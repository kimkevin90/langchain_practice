# LangChain 대화 메모리 시스템

이 문서에서는 LangChain에서 사용되는 두 가지 대화 메모리 시스템, `ConversationBufferMemory`와 `ConversationSummaryMemory`의 차이점과 각각의 특징에 대해 설명합니다.

## `ConversationBufferMemory`

![image](https://github.com/kimkevin90/langchain_practice/assets/65535673/324d8538-6b99-4ec1-b5f4-2f00696b0a75)

### 설명
- `ConversationBufferMemory`는 대화의 모든 메시지를 순서대로 저장하고 관리하는 메모리 시스템입니다.
- 대화 중 발생한 모든 텍스트 내용이 이 시스템에 저장됩니다.

### 예시
```python
memory = ConversationBufferMemory(memory_key='messages', return_messages=True)
```

## `ConversationSummaryMemory`

![image](https://github.com/kimkevin90/langchain_practice/assets/65535673/cfbaab4a-5de1-4100-9aff-f6f16fa99bbd)

### 설명
- `ConversationSummaryMemory`는 대화의 핵심 내용과 요약된 정보를 저장합니다.
- 중요한 정보나 결정적인 대화 포인트를 요약하여 저장하는 시스템입니다.
- 
### 예시
```python
memory = ConversationSummaryMemory(memory_key='messages', return_messages=True, llm=chat)
```

## Conclusion
- ConversationBufferMemory는 대화의 모든 세부 사항을 저장하고 관리하는 반면, ConversationSummaryMemory는 대화의 핵심 요약 정보를 저장합니다.
이는 대화의 맥락을 이해하고 관리하는 방식에서 큰 차이를 만듭니다. ConversationBufferMemory는 데이터가 많아질수록 관리가 복잡해질 수 있지만, ConversationSummaryMemory는 중요한 정보에 집중할 수 있어 긴 대화나 복잡한 대화 상황에서 효과적입니다.
