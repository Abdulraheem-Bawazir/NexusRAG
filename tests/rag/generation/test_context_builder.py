import pytest

from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.rag.generation import ContextBuilder


def make_result(
    chunk_id: str = "chunk-001",
) -> HybridRetrievalResult:
    return HybridRetrievalResult(
        chunk_id=chunk_id,
        document_id="doc-001",
        text="Remote work is allowed.",
        source="policy.pdf",
        file_type="pdf",
        score=0.5,
        metadata={
            "page_number": 4,
        },
    )


def test_context_contains_numbered_source() -> None:
    builder = ContextBuilder()

    context, citations = builder.build(
        [make_result()]
    )

    assert "[1]" in context
    assert "policy.pdf" in context
    assert "Remote work is allowed." in context

    assert len(citations) == 1
    assert citations[0].index == 1
    assert citations[0].source == "policy.pdf"


def test_empty_results_return_empty_context() -> None:
    builder = ContextBuilder()

    context, citations = builder.build([])

    assert context == ""
    assert citations == ()


def test_context_limit_is_respected() -> None:
    builder = ContextBuilder(
        max_chars=200,
    )

    results = [
        make_result("chunk-001"),
        make_result("chunk-002"),
    ]

    context, citations = builder.build(
        results
    )

    assert len(context) <= 200
    assert len(citations) <= 1


def test_invalid_max_chars_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="max_chars must be greater than 0",
    ):
        ContextBuilder(max_chars=0)