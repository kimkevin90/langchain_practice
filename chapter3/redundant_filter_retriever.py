from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever


class RedundantFilterRetriever(BaseRetriever):
    embeddings: Embeddings
    chroma: Chroma

    def get_relevant_documents(self, query):
        # 요청된 query문자열에 대한 응답관련([-1,0]과 같은) 백터 추출
        emb = self.embeddings.embed_query(query)

        # max_marginal_relevance_search_by_vector는 다양한 임베딩을 모두 비교하고 중복되는 임베딩 제거
        return self.chroma.max_marginal_relevance_search_by_vector(
            embedding=emb,
            # 중복에 관한 임계값 설정
            # 1에 가까울 수록 유사한 문서를 허용
            lambda_mult=0.8
        )

    async def aget_relevant_documents(self):
        return []
