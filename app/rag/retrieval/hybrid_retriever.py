from dataclasses import dataclass
from typing import Any, Protocol

from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.models.keyword_retrieval_result import KeywordRetrievalResult
from app.models.retrieval_result import RetrievalResult
from app.rag.retrieval.reranker import Reranker


class SemanticRetrieverProtocol(Protocol):
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[RetrievalResult]:
        ...


class KeywordRetrieverProtocol(Protocol):
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[KeywordRetrievalResult]:
        ...


@dataclass(slots=True)
class _Candidate:
    chunk_id: str
    document_id: str
    text: str
    source: str
    file_type: str
    metadata: dict[str, Any]
    score: float = 0.0
    semantic_rank: int | None = None
    keyword_rank: int | None = None


class HybridRetriever:
    """Fuse semantic and BM25 rankings using RRF."""

    def __init__(
        self,
        semantic_retriever: SemanticRetrieverProtocol,
        keyword_retriever: KeywordRetrieverProtocol,
        rrf_k: int = 60,
        reranker: Reranker | None = None,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError(
                "rrf_k must be greater than 0."
            )

        self.semantic_retriever = semantic_retriever
        self.keyword_retriever = keyword_retriever
        self.rrf_k = rrf_k
        self.reranker = reranker

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        min_keyword_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[HybridRetrievalResult]:
        """Return fused and optionally reranked results."""

        if not query.strip():
            raise ValueError("query cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        candidate_k = top_k * 2

        semantic_results = (
            self.semantic_retriever.retrieve(
                query=query,
                top_k=candidate_k,
                max_distance=max_distance,
                document_id=document_id,
                source=source,
                file_type=file_type,
            )
        )

        keyword_results = (
            self.keyword_retriever.retrieve(
                query=query,
                top_k=candidate_k,
                min_score=min_keyword_score,
                document_id=document_id,
                source=source,
                file_type=file_type,
            )
        )

        candidates: dict[str, _Candidate] = {}

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            candidate = candidates.setdefault(
                result.chunk_id,
                _Candidate(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    text=result.text,
                    source=result.source,
                    file_type=result.file_type,
                    metadata=dict(result.metadata),
                ),
            )

            candidate.semantic_rank = rank
            candidate.score += (
                1.0 / (self.rrf_k + rank)
            )

        for rank, result in enumerate(
            keyword_results,
            start=1,
        ):
            candidate = candidates.setdefault(
                result.chunk_id,
                _Candidate(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    text=result.text,
                    source=result.source,
                    file_type=result.file_type,
                    metadata=dict(result.metadata),
                ),
            )

            candidate.keyword_rank = rank
            candidate.score += (
                1.0 / (self.rrf_k + rank)
            )

        results = [
            HybridRetrievalResult(
                chunk_id=candidate.chunk_id,
                document_id=candidate.document_id,
                text=candidate.text,
                source=candidate.source,
                file_type=candidate.file_type,
                score=candidate.score,
                semantic_rank=candidate.semantic_rank,
                keyword_rank=candidate.keyword_rank,
                metadata=dict(candidate.metadata),
            )
            for candidate in candidates.values()
        ]

        results.sort(
            key=lambda result: (
                -result.score,
                result.chunk_id,
            )
        )

        if self.reranker is not None:
            return self.reranker.rerank(
                query=query,
                results=results,
                top_k=top_k,
            )

        return results[:top_k]