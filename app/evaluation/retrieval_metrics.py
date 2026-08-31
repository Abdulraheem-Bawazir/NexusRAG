from collections.abc import Mapping, Sequence

from app.evaluation.models import (
    RetrievalEvaluationCase,
    RetrievalMetrics,
)


def hit_at_k(
    expected_chunk_ids: set[str] | frozenset[str],
    ranked_chunk_ids: Sequence[str],
    k: int,
) -> float:
    """Return 1 when at least one expected chunk appears in top-k."""

    if k <= 0:
        raise ValueError(
            "k must be greater than 0."
        )

    if not expected_chunk_ids:
        raise ValueError(
            "expected_chunk_ids cannot be empty."
        )

    retrieved = set(
        ranked_chunk_ids[:k]
    )

    return float(
        bool(
            expected_chunk_ids
            & retrieved
        )
    )


def recall_at_k(
    expected_chunk_ids: set[str] | frozenset[str],
    ranked_chunk_ids: Sequence[str],
    k: int,
) -> float:
    """Return fraction of expected chunks recovered in top-k."""

    if k <= 0:
        raise ValueError(
            "k must be greater than 0."
        )

    if not expected_chunk_ids:
        raise ValueError(
            "expected_chunk_ids cannot be empty."
        )

    retrieved = set(
        ranked_chunk_ids[:k]
    )

    relevant_retrieved = (
        expected_chunk_ids
        & retrieved
    )

    return (
        len(relevant_retrieved)
        / len(expected_chunk_ids)
    )


def reciprocal_rank(
    expected_chunk_ids: set[str] | frozenset[str],
    ranked_chunk_ids: Sequence[str],
) -> float:
    """Return reciprocal rank of the first relevant result."""

    if not expected_chunk_ids:
        raise ValueError(
            "expected_chunk_ids cannot be empty."
        )

    for rank, chunk_id in enumerate(
        ranked_chunk_ids,
        start=1,
    ):
        if chunk_id in expected_chunk_ids:
            return 1.0 / rank

    return 0.0


def evaluate_retrieval(
    cases: Sequence[RetrievalEvaluationCase],
    ranked_results: Mapping[str, Sequence[str]],
    k: int = 5,
) -> RetrievalMetrics:
    """Evaluate retrieval results over multiple queries."""

    if not cases:
        raise ValueError(
            "At least one evaluation case is required."
        )

    if k <= 0:
        raise ValueError(
            "k must be greater than 0."
        )

    hit_scores: list[float] = []
    recall_scores: list[float] = []
    reciprocal_ranks: list[float] = []

    for case in cases:
        ranking = ranked_results.get(
            case.query,
            (),
        )

        hit_scores.append(
            hit_at_k(
                case.expected_chunk_ids,
                ranking,
                k,
            )
        )

        recall_scores.append(
            recall_at_k(
                case.expected_chunk_ids,
                ranking,
                k,
            )
        )

        reciprocal_ranks.append(
            reciprocal_rank(
                case.expected_chunk_ids,
                ranking,
            )
        )

    count = len(cases)

    return RetrievalMetrics(
        hit_rate_at_k=(
            sum(hit_scores) / count
        ),
        recall_at_k=(
            sum(recall_scores) / count
        ),
        mrr=(
            sum(reciprocal_ranks)
            / count
        ),
        case_count=count,
    )