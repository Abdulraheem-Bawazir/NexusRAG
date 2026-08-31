from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationCase:
    """Expected retrieval behavior for one evaluation query."""

    query: str
    expected_chunk_ids: frozenset[str]

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError(
                "Evaluation query cannot be empty."
            )

        if not self.expected_chunk_ids:
            raise ValueError(
                "expected_chunk_ids cannot be empty."
            )


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    """Aggregate retrieval evaluation metrics."""

    hit_rate_at_k: float
    recall_at_k: float
    mrr: float
    case_count: int

    def __post_init__(self) -> None:
        for value in (
            self.hit_rate_at_k,
            self.recall_at_k,
            self.mrr,
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    "Metric values must be between 0 and 1."
                )

        if self.case_count <= 0:
            raise ValueError(
                "case_count must be greater than 0."
            )