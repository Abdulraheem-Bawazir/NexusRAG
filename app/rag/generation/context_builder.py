import json
from copy import deepcopy

from app.models.citation import SourceCitation
from app.models.hybrid_retrieval_result import HybridRetrievalResult


class ContextBuilder:
    """Convert retrieved evidence into numbered LLM context."""

    def __init__(
        self,
        max_chars: int = 12000,
    ) -> None:
        if max_chars <= 0:
            raise ValueError(
                "max_chars must be greater than 0."
            )

        self.max_chars = max_chars

    def build(
        self,
        results: list[HybridRetrievalResult],
    ) -> tuple[str, tuple[SourceCitation, ...]]:
        if not results:
            return "", ()

        blocks: list[str] = []
        citations: list[SourceCitation] = []
        current_length = 0

        for result in results:
            citation_index = len(citations) + 1

            metadata_json = json.dumps(
                result.metadata,
                ensure_ascii=True,
                sort_keys=True,
            )

            block = (
                f"[{citation_index}]\n"
                f"Source: {result.source}\n"
                f"Document ID: {result.document_id}\n"
                f"File type: {result.file_type}\n"
                f"Metadata: {metadata_json}\n"
                "Content:\n"
                f"{result.text}"
            )

            separator_length = 2 if blocks else 0

            projected_length = (
                current_length
                + separator_length
                + len(block)
            )

            if projected_length > self.max_chars:
                break

            blocks.append(block)

            citations.append(
                SourceCitation(
                    index=citation_index,
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    source=result.source,
                    file_type=result.file_type,
                    metadata=deepcopy(result.metadata),
                )
            )

            current_length = projected_length

        return (
            "\n\n".join(blocks),
            tuple(citations),
        )