from dataclasses import dataclass

from app.models.citation import SourceCitation


@dataclass(frozen=True, slots=True)
class RAGAnswer:
    """Grounded answer returned by the RAG pipeline."""

    answer: str
    citations: tuple[SourceCitation, ...]
    insufficient_evidence: bool = False

    def __post_init__(self) -> None:
        if not self.answer.strip():
            raise ValueError(
                "RAG answer cannot be empty."
            )