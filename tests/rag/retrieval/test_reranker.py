import pytest

from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.rag.retrieval import NoOpReranker, Reranker


def make_result(
    chunk_id: str,
    score: float,
) -> HybridRetrievalResult:
    return HybridRetrievalResult(
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        text=f"Text for {chunk_id}",
        source=f"{chunk_id}.txt",
        file_type="txt",
        score=score,
    )


def test_noop_reranker_matches_protocol() -> None:
    reranker = NoOpReranker()

    assert isinstance(reranker, Reranker)


def test_noop_reranker_preserves_order() -> None:
    reranker = NoOpReranker()

    results = [
        make_result("chunk-a", 0.9),
        make_result("chunk-b", 0.8),
        make_result("chunk-c", 0.7),
    ]

    reranked = reranker.rerank(
        query="example query",
        results=results,
        top_k=3,
    )

    assert [
        result.chunk_id
        for result in reranked
    ] == [
        "chunk-a",
        "chunk-b",
        "chunk-c",
    ]


def test_noop_reranker_respects_top_k() -> None:
    reranker = NoOpReranker()

    results = [
        make_result("chunk-a", 0.9),
        make_result("chunk-b", 0.8),
        make_result("chunk-c", 0.7),
    ]

    reranked = reranker.rerank(
        query="example",
        results=results,
        top_k=2,
    )

    assert len(reranked) == 2


def test_empty_query_is_rejected() -> None:
    reranker = NoOpReranker()

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        reranker.rerank(
            query="   ",
            results=[],
            top_k=5,
        )


def test_invalid_top_k_is_rejected() -> None:
    reranker = NoOpReranker()

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        reranker.rerank(
            query="example",
            results=[],
            top_k=0,
        )