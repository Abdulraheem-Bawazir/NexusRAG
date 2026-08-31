import pytest

from app.models.chunk import Chunk
from app.rag.retrieval import KeywordRetriever


def make_chunk(
    chunk_id: str,
    document_id: str,
    text: str,
    source: str,
) -> Chunk:
    return Chunk(
        id=chunk_id,
        document_id=document_id,
        text=text,
        chunk_index=0,
        source=source,
        file_type="txt",
        metadata={"department": "test"},
    )


def create_retriever() -> KeywordRetriever:
    chunks = [
        make_chunk(
            "chunk-remote",
            "doc-remote",
            (
                "Employees may work remotely "
                "three days per week."
            ),
            "remote_policy.txt",
        ),
        make_chunk(
            "chunk-security",
            "doc-security",
            (
                "Password rotation and "
                "multi-factor authentication "
                "are mandatory."
            ),
            "security_policy.txt",
        ),
        make_chunk(
            "chunk-vacation",
            "doc-vacation",
            (
                "Employees receive twenty-five "
                "days of annual vacation leave."
            ),
            "vacation_policy.txt",
        ),
    ]

    return KeywordRetriever(chunks)


def test_keyword_retrieval_returns_matching_chunk() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "password authentication",
        top_k=1,
    )

    assert len(results) == 1
    assert (
        results[0].chunk_id
        == "chunk-security"
    )
    assert (
        results[0].source
        == "security_policy.txt"
    )


def test_keyword_retrieval_supports_top_k() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "employees",
        top_k=2,
    )

    assert len(results) == 2


def test_keyword_result_contains_score() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "password",
        top_k=1,
    )

    assert len(results) == 1
    assert isinstance(
        results[0].score,
        float,
    )


def test_empty_query_is_rejected() -> None:
    retriever = create_retriever()

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        retriever.retrieve("   ")


def test_invalid_top_k_is_rejected() -> None:
    retriever = create_retriever()

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        retriever.retrieve(
            "password",
            top_k=0,
        )


def test_empty_index_returns_no_results() -> None:
    retriever = KeywordRetriever([])

    assert retriever.retrieve(
        "anything"
    ) == []


def test_document_filter_is_supported() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "employees",
        document_id="doc-vacation",
    )

    assert len(results) == 1
    assert (
        results[0].document_id
        == "doc-vacation"
    )


def test_source_filter_is_supported() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "employees",
        source="remote_policy.txt",
    )

    assert len(results) == 1
    assert (
        results[0].source
        == "remote_policy.txt"
    )


def test_file_type_filter_is_supported() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "employees",
        file_type=".TXT",
    )

    assert results
    assert all(
        result.file_type == "txt"
        for result in results
    )


def test_min_score_can_filter_results() -> None:
    retriever = create_retriever()

    results = retriever.retrieve(
        "password",
        min_score=999.0,
    )

    assert results == []