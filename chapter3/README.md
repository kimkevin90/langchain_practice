# LangChain 텍스트 로딩 및 분할 시스템

LangChain을 사용하여 텍스트 문서를 로드하고 분할하는 방법에 대해 설명합니다.

## 구성 요소

1. **`TextLoader`**
   - `TextLoader`는 파일 시스템에서 텍스트 파일을 로드하는 데 사용됩니다.
   - 이 예시에서는 `"facts.txt"`라는 파일을 로드하는 데 사용됩니다.

2. **`CharacterTextSplitter`**
   - `CharacterTextSplitter`는 텍스트를 특정 크기의 청크로 분할하는 데 사용됩니다.
   - 여기서는 청크 사이즈를 200자로 설정하고, 청크 간의 중복은 없도록 설정합니다(`chunk_size=200, chunk_overlap=0`).

3. **임베딩 생성**:
   - `OpenAIEmbeddings`를 사용하여 분할된 텍스트 청크를 임베딩(벡터) 형태로 변환합니다.

4. **Chroma 벡터 저장소 생성**:
   - `Chroma.from_documents` 메서드를 사용하여 문서들과 임베딩을 기반으로 벡터 저장소를 생성합니다.
   - `persist_directory="emb"` 옵션은 생성된 벡터 저장소를 `"emb"` 디렉토리에 지속적으로 저장합니다.

5. **유사도 검색 수행**:
   - `db.similarity_search` 메서드를 사용하여 특정 질문에 대한 유사한 내용을 포함하는 문서를 검색합니다.

# LangChain Retriever

벡터스토어에 저장된 임베딩을 바탕으로 Retriever를 사용하여 질의에 대한 응답 문장을 생성합니다.

1. **벡터스토어에서 임베딩 불러오기**
   - `Chroma`는 파일 시스템에서 emb 디렉토리의 임베딩을 불러옵니다.

2. **커스텀 RedundantFilterRetriever 생성**
   - `RedundantFilter`를 사용시, 임베딩 벡터 계산을 중복으로 진행하므로, 커스텀 RedundantFilterRetriever를 생성하여 요청된 질의에 적합한 임베딩을 불러옵니다.
   - `max_marginal_relevance_search_by_vector`를 사용하여 불러온 임베딩 및 중복 임계값을 설정합니다.

3. **ChatOpenAI를 사용하여 응답**
   - 질의 응답시 RedundantFilterRetriever를 통해 벡터스토어를 참조하여 응답할 수 있도록 합니다.