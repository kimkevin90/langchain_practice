# LangChain을 활용한 OpenAIFunctionsAgent와 AgentExecutor 사용 예시

이 문서에서는 LangChain 라이브러리를 사용하여 OpenAI의 언어 모델을 기반으로 하는 `OpenAIFunctionsAgent`와 `AgentExecutor`를 활용하는 방법을 설명합니다.

## OpenAIFunctionsAgent

`OpenAIFunctionsAgent`는 OpenAI의 언어 모델을 활용하여 입력된 텍스트를 처리하고, 다양한 도구를 사용하여 작업을 수행합니다.

### 주요 기능

- **챗봇 생성**: OpenAI의 언어 모델을 기반으로 한 챗봇을 생성합니다.
- **프롬프트 설정**: 대화형 프롬프트를 구성하여 사용자의 메시지와 에이전트의 작업 결과를 포함합니다.
- **도구 등록**: SQLite 데이터베이스 쿼리를 실행할 수 있는 `run_query_tool` 도구를 등록합니다.

## AgentExecutor

`AgentExecutor`는 `OpenAIFunctionsAgent`를 실행하고 사용자의 요청에 대한 처리를 관리합니다.

### 주요 기능

- **에이전트 실행**: `OpenAIFunctionsAgent` 인스턴스를 사용합니다.
- **상세 로깅**: 실행 로그를 상세하게 표시합니다.
- **도구 사용**: 외부 도구(예: `run_query_tool`)를 활용합니다.

## 작동 과정

1. **질문 처리**: 사용자의 질문을 `OpenAIFunctionsAgent`로 전달합니다.
2. **프롬프트 구성 및 실행**: 설정된 프롬프트를 기반으로 질문을 처리하고 필요한 작업을 식별합니다.
3. **도구 사용**: 필요한 경우 `run_query_tool`이 데이터베이스 쿼리를 실행합니다.
4. **결과 제공**: 쿼리 실행 결과를 사용자에게 답변 형식으로 제공합니다.
