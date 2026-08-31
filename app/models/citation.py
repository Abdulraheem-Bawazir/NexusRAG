from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceCitation:
    """Traceable source attached to a generated answer."""

    index: int
    chunk_id: str
    document_id: str
    source: str
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.index <= 0:
            raise ValueError(
                "Citation index must be greater than 0."
            )

        if not self.chunk_id.strip():
            raise ValueError(
                "Citation chunk_id cannot be empty."
            )

        if not self.document_id.strip():
            raise ValueError(
                "Citation document_id cannot be empty."
            )

        if not self.source.strip():
            raise ValueError(
                "Citation source cannot be empty."
            )