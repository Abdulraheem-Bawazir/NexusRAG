from typing import Protocol, runtime_checkable

from app.models.hybrid_retrieval_result import HybridRetrievalResult


@runtime_checkable
class Reranker(Protocol):
    """Contract for optional retrieval reranking strategies."""

    def rerank(
        self,
        query: str,
        results: list[HybridRetrievalResult],
        top_k: int,
    ) -> list[HybridRetrievalResult]:
        ...


class NoOpReranker:
    """Preserve the existing retrieval order."""

    def rerank(
        self,
        query: str,
        results: list[HybridRetrievalResult],
        top_k: int,
    ) -> list[HybridRetrievalResult]:
        if not query.strip():
            raise ValueError("query cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        return results[:top_k]