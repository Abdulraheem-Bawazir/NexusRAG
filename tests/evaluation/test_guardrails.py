from app.evaluation import (
    answerable_question_handled_correctly,
    unsupported_question_handled_correctly,
)
from app.models.citation import SourceCitation
from app.models.rag_answer import RAGAnswer


def make_citation() -> SourceCitation:
    return SourceCitation(
        index=1,
        chunk_id="chunk-001",
        document_id="doc-001",
        source="policy.txt",
        file_type="txt",
    )


def test_supported_answer_requires_citation() -> None:
    answer = RAGAnswer(
        answer="Remote work is allowed.",
        citations=(
            make_citation(),
        ),
    )

    assert (
        answerable_question_handled_correctly(
            answer
        )
    )


def test_supported_answer_without_citation_is_invalid() -> None:
    answer = RAGAnswer(
        answer="Remote work is allowed.",
        citations=(),
    )

    assert not (
        answerable_question_handled_correctly(
            answer
        )
    )


def test_unsupported_question_requires_insufficient_evidence() -> None:
    answer = RAGAnswer(
        answer="Not enough evidence.",
        citations=(),
        insufficient_evidence=True,
    )

    assert (
        unsupported_question_handled_correctly(
            answer
        )
    )


def test_unsupported_answer_with_citation_is_invalid() -> None:
    answer = RAGAnswer(
        answer="Not enough evidence.",
        citations=(
            make_citation(),
        ),
        insufficient_evidence=True,
    )

    assert not (
        unsupported_question_handled_correctly(
            answer
        )
    )