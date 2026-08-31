from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.models.keyword_retrieval_result import KeywordRetrievalResult
from app.models.retrieval_result import RetrievalResult
from app.rag.retrieval import HybridRetriever


class FakeSemanticRetriever:
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[RetrievalResult]:
        return [
            RetrievalResult(
                chunk_id="chunk-a",
                document_id="doc-a",
                text="Semantic result A",
                source="a.txt",
                file_type="txt",
                distance=0.1,
            ),
            RetrievalResult(
                chunk_id="chunk-b",
                document_id="doc-b",
                text="Semantic result B",
                source="b.txt",
                file_type="txt",
                distance=0.2,
            ),
        ]


class FakeKeywordRetriever:
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[KeywordRetrievalResult]:
        return []


class ReverseReranker:
    def rerank(
        self,
        query: str,
        results: list[HybridRetrievalResult],
        top_k: int,
    ) -> list[HybridRetrievalResult]:
        return list(
            reversed(results)
        )[:top_k]


def test_hybrid_retriever_uses_configured_reranker() -> None:
    retriever = HybridRetriever(
        semantic_retriever=FakeSemanticRetriever(),
        keyword_retriever=FakeKeywordRetriever(),
        reranker=ReverseReranker(),
    )

    results = retriever.retrieve(
        "example query",
        top_k=2,
    )

    assert [
        result.chunk_id
        for result in results
    ] == [
        "chunk-b",
        "chunk-a",
    ]