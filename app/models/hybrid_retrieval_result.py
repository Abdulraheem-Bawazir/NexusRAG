from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class HybridRetrievalResult:
    """A chunk ranked by fused semantic and keyword retrieval."""

    chunk_id: str
    document_id: str
    text: str
    source: str
    file_type: str
    score: float
    semantic_rank: int | None = None
    keyword_rank: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError("chunk_id cannot be empty.")

        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty.")

        if not self.text.strip():
            raise ValueError("text cannot be empty.")

        if not self.source.strip():
            raise ValueError("source cannot be empty.")

        if self.score <= 0:
            raise ValueError("score must be greater than 0.")

        if (
            self.semantic_rank is not None
            and self.semantic_rank <= 0
        ):
            raise ValueError(
                "semantic_rank must be greater than 0."
            )

        if (
            self.keyword_rank is not None
            and self.keyword_rank <= 0
        ):
            raise ValueError(
                "keyword_rank must be greater than 0."
            )