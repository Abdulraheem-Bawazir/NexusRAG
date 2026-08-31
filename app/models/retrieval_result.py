from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """A ranked chunk returned by the retrieval system."""

    chunk_id: str
    document_id: str
    text: str
    source: str
    file_type: str
    distance: float
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

        if self.distance < 0:
            raise ValueError("distance cannot be negative.")