from dataclasses import dataclass, field
from typing import Any

SUPPORTED_FILE_TYPES = {"pdf", "docx", "txt"}


@dataclass(slots=True)

##automatically gives us things like an initializer.##

class Document:
    """Normalized representation of an ingested document."""

    id: str
    text: str
    source: str
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate document fields after initialization."""

        if not self.id.strip():
            raise ValueError("Document id cannot be empty.")

        if not self.text.strip():
            raise ValueError("Document text cannot be empty.")

        if not self.source.strip():
            raise ValueError("Document source cannot be empty.")

        normalized_file_type = self.file_type.lower().strip()

        if normalized_file_type not in SUPPORTED_FILE_TYPES:
            raise ValueError(
                f"Unsupported file type: {self.file_type}. "
                f"Supported types: {sorted(SUPPORTED_FILE_TYPES)}"
            )

        self.file_type = normalized_file_type