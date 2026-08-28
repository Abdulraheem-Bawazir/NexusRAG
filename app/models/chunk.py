from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Chunk:
    """A retrieval-ready piece of a source document."""

    id: str
    document_id: str
    text: str
    chunk_index: int
    source: str
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Chunk id cannot be empty.")

        if not self.document_id.strip():
            raise ValueError("Document id cannot be empty.")

        if not self.text.strip():
            raise ValueError("Chunk text cannot be empty.")

        if self.chunk_index < 0:
            raise ValueError("Chunk index cannot be negative.")

        if not self.source.strip():
            raise ValueError("Chunk source cannot be empty.")

        normalized_file_type = self.file_type.lower().lstrip(".")

        if normalized_file_type not in {"pdf", "docx", "txt"}:
            raise ValueError(
                f"Unsupported file type: {self.file_type}"
            )

        object.__setattr__(self, "file_type", normalized_file_type)