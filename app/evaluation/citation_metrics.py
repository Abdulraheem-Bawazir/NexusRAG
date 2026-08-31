from collections.abc import Iterable

from app.models.rag_answer import RAGAnswer


def citation_precision(
    answer: RAGAnswer,
    expected_sources: Iterable[str],
) -> float:
    """Measure how many returned citations point to expected sources."""

    expected = set(
        expected_sources
    )

    cited = {
        citation.source
        for citation in answer.citations
    }

    if not cited:
        return 0.0

    correct = cited & expected

    return len(correct) / len(cited)


def citation_recall(
    answer: RAGAnswer,
    expected_sources: Iterable[str],
) -> float:
    """Measure how many expected sources were actually cited."""

    expected = set(
        expected_sources
    )

    if not expected:
        raise ValueError(
            "expected_sources cannot be empty."
        )

    cited = {
        citation.source
        for citation in answer.citations
    }

    correct = cited & expected

    return len(correct) / len(expected)


def citation_f1(
    answer: RAGAnswer,
    expected_sources: Iterable[str],
) -> float:
    """Return harmonic mean of citation precision and recall."""

    expected = tuple(
        expected_sources
    )

    precision = citation_precision(
        answer,
        expected,
    )

    recall = citation_recall(
        answer,
        expected,
    )

    if precision + recall == 0:
        return 0.0

    return (
        2
        * precision
        * recall
        / (precision + recall)
    )