import pytest

from app.models.keyword_retrieval_result import KeywordRetrievalResult
from app.models.retrieval_result import RetrievalResult
from app.rag.retrieval import HybridRetriever


def semantic_result(
    chunk_id: str,
    distance: float,
) -> RetrievalResult:
    return RetrievalResult(
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        text=f"Text for {chunk_id}",
        source=f"{chunk_id}.txt",
        file_type="txt",
        distance=distance,
        metadata={"type": "semantic"},
    )


def keyword_result(
    chunk_id: str,
    score: float,
) -> KeywordRetrievalResult:
    return KeywordRetrievalResult(
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        text=f"Text for {chunk_id}",
        source=f"{chunk_id}.txt",
        file_type="txt",
        score=score,
        metadata={"type": "keyword"},
    )


class FakeSemanticRetriever:
    def __init__(
        self,
        results: list[RetrievalResult],
    ) -> None:
        self.results = results
        self.last_kwargs = None

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[RetrievalResult]:
        self.last_kwargs = {
            "query": query,
            "top_k": top_k,
            "max_distance": max_distance,
            "document_id": document_id,
            "source": source,
            "file_type": file_type,
        }

        return self.results[:top_k]


class FakeKeywordRetriever:
    def __init__(
        self,
        results: list[KeywordRetrievalResult],
    ) -> None:
        self.results = results
        self.last_kwargs = None

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[KeywordRetrievalResult]:
        self.last_kwargs = {
            "query": query,
            "top_k": top_k,
            "min_score": min_score,
            "document_id": document_id,
            "source": source,
            "file_type": file_type,
        }

        return self.results[:top_k]


def test_chunk_found_by_both_retrievers_is_boosted() -> None:
    semantic = FakeSemanticRetriever(
        [
            semantic_result("chunk-a", 0.1),
            semantic_result("chunk-b", 0.2),
        ]
    )

    keyword = FakeKeywordRetriever(
        [
            keyword_result("chunk-b", 4.0),
            keyword_result("chunk-c", 3.0),
        ]
    )

    retriever = HybridRetriever(
        semantic_retriever=semantic,
        keyword_retriever=keyword,
    )

    results = retriever.retrieve(
        "example query",
        top_k=3,
    )

    assert results[0].chunk_id == "chunk-b"

    assert results[0].semantic_rank == 2
    assert results[0].keyword_rank == 1


def test_results_from_only_one_retriever_are_preserved() -> None:
    semantic = FakeSemanticRetriever(
        [
            semantic_result("chunk-a", 0.1),
        ]
    )

    keyword = FakeKeywordRetriever(
        [
            keyword_result("chunk-b", 5.0),
        ]
    )

    retriever = HybridRetriever(
        semantic_retriever=semantic,
        keyword_retriever=keyword,
    )

    results = retriever.retrieve(
        "example",
        top_k=2,
    )

    ids = {
        result.chunk_id
        for result in results
    }

    assert ids == {
        "chunk-a",
        "chunk-b",
    }


def test_top_k_limits_fused_results() -> None:
    semantic = FakeSemanticRetriever(
        [
            semantic_result("chunk-a", 0.1),
            semantic_result("chunk-b", 0.2),
            semantic_result("chunk-c", 0.3),
        ]
    )

    keyword = FakeKeywordRetriever([])

    retriever = HybridRetriever(
        semantic_retriever=semantic,
        keyword_retriever=keyword,
    )

    results = retriever.retrieve(
        "example",
        top_k=2,
    )

    assert len(results) == 2


def test_filters_are_forwarded_to_both_retrievers() -> None:
    semantic = FakeSemanticRetriever([])
    keyword = FakeKeywordRetriever([])

    retriever = HybridRetriever(
        semantic_retriever=semantic,
        keyword_retriever=keyword,
    )

    retriever.retrieve(
        "policy",
        top_k=3,
        max_distance=0.5,
        min_keyword_score=1.0,
        document_id="doc-001",
        source="policy.pdf",
        file_type="pdf",
    )

    assert semantic.last_kwargs == {
        "query": "policy",
        "top_k": 6,
        "max_distance": 0.5,
        "document_id": "doc-001",
        "source": "policy.pdf",
        "file_type": "pdf",
    }

    assert keyword.last_kwargs == {
        "query": "policy",
        "top_k": 6,
        "min_score": 1.0,
        "document_id": "doc-001",
        "source": "policy.pdf",
        "file_type": "pdf",
    }


def test_empty_query_is_rejected() -> None:
    retriever = HybridRetriever(
        semantic_retriever=FakeSemanticRetriever([]),
        keyword_retriever=FakeKeywordRetriever([]),
    )

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        retriever.retrieve("   ")


def test_invalid_top_k_is_rejected() -> None:
    retriever = HybridRetriever(
        semantic_retriever=FakeSemanticRetriever([]),
        keyword_retriever=FakeKeywordRetriever([]),
    )

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        retriever.retrieve(
            "query",
            top_k=0,
        )


def test_invalid_rrf_k_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="rrf_k must be greater than 0",
    ):
        HybridRetriever(
            semantic_retriever=FakeSemanticRetriever([]),
            keyword_retriever=FakeKeywordRetriever([]),
            rrf_k=0,
        )