import pytest

from app.evaluation import (
    citation_f1,
    citation_precision,
    citation_recall,
)
from app.models.citation import SourceCitation
from app.models.rag_answer import RAGAnswer


def make_citation(
    index: int,
    source: str,
) -> SourceCitation:
    return SourceCitation(
        index=index,
        chunk_id=f"chunk-{index}",
        document_id=f"doc-{index}",
        source=source,
        file_type="txt",
    )


def test_perfect_citation_metrics() -> None:
    answer = RAGAnswer(
        answer="Grounded answer.",
        citations=(
            make_citation(
                1,
                "policy.txt",
            ),
        ),
    )

    expected = {
        "policy.txt"
    }

    assert (
        citation_precision(
            answer,
            expected,
        )
        == 1.0
    )

    assert (
        citation_recall(
            answer,
            expected,
        )
        == 1.0
    )

    assert (
        citation_f1(
            answer,
            expected,
        )
        == 1.0
    )


def test_incorrect_extra_citation_reduces_precision() -> None:
    answer = RAGAnswer(
        answer="Grounded answer.",
        citations=(
            make_citation(
                1,
                "policy.txt",
            ),
            make_citation(
                2,
                "wrong.txt",
            ),
        ),
    )

    score = citation_precision(
        answer,
        {"policy.txt"},
    )

    assert score == 0.5


def test_missing_expected_source_reduces_recall() -> None:
    answer = RAGAnswer(
        answer="Grounded answer.",
        citations=(
            make_citation(
                1,
                "policy.txt",
            ),
        ),
    )

    score = citation_recall(
        answer,
        {
            "policy.txt",
            "handbook.txt",
        },
    )

    assert score == 0.5


def test_no_citations_have_zero_precision() -> None:
    answer = RAGAnswer(
        answer="No evidence.",
        citations=(),
        insufficient_evidence=True,
    )

    assert (
        citation_precision(
            answer,
            {"policy.txt"},
        )
        == 0.0
    )


def test_empty_expected_sources_are_rejected_for_recall() -> None:
    answer = RAGAnswer(
        answer="Answer.",
        citations=(),
    )

    with pytest.raises(
        ValueError,
        match="expected_sources cannot be empty",
    ):
        citation_recall(
            answer,
            [],
        )