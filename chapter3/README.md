# LangChain 텍스트 로딩 및 분할 시스템

이 문서에서는 LangChain을 사용하여 텍스트 문서를 로드하고 분할하는 방법에 대해 설명합니다.

## 구성 요소

1. **`TextLoader`**
   - `TextLoader`는 파일 시스템에서 텍스트 파일을 로드하는 데 사용됩니다.
   - 이 예시에서는 `"facts.txt"`라는 파일을 로드하는 데 사용됩니다.

2. **`CharacterTextSplitter`**
   - `CharacterTextSplitter`는 텍스트를 특정 크기의 청크로 분할하는 데 사용됩니다.
   - 여기서는 청크 사이즈를 200자로 설정하고, 청크 간의 중복은 없도록 설정합니다(`chunk_size=200, chunk_overlap=0`).
