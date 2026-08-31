from typing import Protocol

from app.models.retrieval_result import RetrievalResult
from app.rag.embeddings.base import EmbeddingProvider


class VectorStore(Protocol):
    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[dict]:
        ...


class SemanticRetriever:
    """Retrieve semantically relevant chunks for a user query."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("query cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        if (
            max_distance is not None
            and max_distance < 0
        ):
            raise ValueError(
                "max_distance cannot be negative."
            )

        filters: dict[str, str] = {}

        if document_id is not None:
            if not document_id.strip():
                raise ValueError(
                    "document_id filter cannot be empty."
                )

            filters["document_id"] = document_id

        if source is not None:
            if not source.strip():
                raise ValueError(
                    "source filter cannot be empty."
                )

            filters["source"] = source

        if file_type is not None:
            normalized_file_type = (
                file_type.lower().lstrip(".")
            )

            if normalized_file_type not in {
                "pdf",
                "docx",
                "txt",
            }:
                raise ValueError(
                    "Unsupported file_type filter."
                )

            filters["file_type"] = (
                normalized_file_type
            )

        query_vector = (
            self.embedding_provider.embed_text(
                query
            )
        )

        matches = self.vector_store.query(
            vector=query_vector,
            top_k=top_k,
            filters=filters or None,
        )

        results = [
            RetrievalResult(
                chunk_id=match["chunk_id"],
                document_id=match["document_id"],
                text=match["text"],
                source=match["source"],
                file_type=match["file_type"],
                distance=match["distance"],
                metadata=match["metadata"],
            )
            for match in matches
        ]

        if max_distance is not None:
            results = [
                result
                for result in results
                if result.distance
                <= max_distance
            ]

        return results