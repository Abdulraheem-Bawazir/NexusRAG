import pytest

from app.evaluation import (
    RetrievalEvaluationCase,
    evaluate_retrieval,
    hit_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_hit_at_k_returns_one_when_relevant_result_exists() -> None:
    score = hit_at_k(
        {"chunk-b"},
        [
            "chunk-a",
            "chunk-b",
        ],
        k=2,
    )

    assert score == 1.0


def test_hit_at_k_returns_zero_when_result_is_missing() -> None:
    score = hit_at_k(
        {"chunk-c"},
        [
            "chunk-a",
            "chunk-b",
        ],
        k=2,
    )

    assert score == 0.0


def test_recall_at_k_handles_multiple_expected_chunks() -> None:
    score = recall_at_k(
        {
            "chunk-a",
            "chunk-c",
        },
        [
            "chunk-a",
            "chunk-b",
        ],
        k=2,
    )

    assert score == 0.5


def test_reciprocal_rank_uses_first_relevant_result() -> None:
    score = reciprocal_rank(
        {"chunk-c"},
        [
            "chunk-a",
            "chunk-b",
            "chunk-c",
        ],
    )

    assert score == pytest.approx(
        1 / 3
    )


def test_reciprocal_rank_returns_zero_when_missing() -> None:
    assert (
        reciprocal_rank(
            {"chunk-c"},
            [
                "chunk-a",
                "chunk-b",
            ],
        )
        == 0.0
    )


def test_evaluate_retrieval_aggregates_metrics() -> None:
    cases = [
        RetrievalEvaluationCase(
            query="remote work",
            expected_chunk_ids=frozenset(
                {"remote"}
            ),
        ),
        RetrievalEvaluationCase(
            query="security",
            expected_chunk_ids=frozenset(
                {"security"}
            ),
        ),
    ]

    rankings = {
        "remote work": [
            "remote",
            "security",
        ],
        "security": [
            "remote",
            "security",
        ],
    }

    metrics = evaluate_retrieval(
        cases,
        rankings,
        k=2,
    )

    assert metrics.hit_rate_at_k == 1.0
    assert metrics.recall_at_k == 1.0
    assert metrics.mrr == 0.75
    assert metrics.case_count == 2


def test_invalid_k_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="k must be greater than 0",
    ):
        hit_at_k(
            {"chunk"},
            [],
            k=0,
        )


def test_empty_evaluation_cases_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="At least one evaluation case",
    ):
        evaluate_retrieval(
            [],
            {},
        )