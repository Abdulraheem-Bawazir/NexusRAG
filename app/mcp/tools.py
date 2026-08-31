from typing import Any, Protocol

from app.models.document import Document
from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.models.rag_answer import RAGAnswer


class NexusRAGEngineProtocol(Protocol):
    def list_documents(
        self,
    ) -> list[Document]:
        ...

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        min_keyword_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[HybridRetrievalResult]:
        ...

    def ask(
        self,
        question: str,
        top_k: int = 5,
        max_distance: float | None = None,
        min_keyword_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> RAGAnswer:
        ...


class MCPToolService:
    """Convert NexusRAG application operations into MCP-safe data."""

    def __init__(
        self,
        engine: NexusRAGEngineProtocol,
    ) -> None:
        self.engine = engine

    def list_documents(
        self,
    ) -> list[dict[str, Any]]:
        documents = (
            self.engine.list_documents()
        )

        return [
            {
                "id": document.id,
                "source": document.source,
                "file_type": document.file_type,
                "metadata": document.metadata,
            }
            for document in documents
        ]

    def search_documents(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[dict[str, Any]]:
        results = self.engine.search(
            query=query,
            top_k=top_k,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )

        return [
            {
                "rank": rank,
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "text": result.text,
                "source": result.source,
                "file_type": result.file_type,
                "score": result.score,
                "semantic_rank": result.semantic_rank,
                "keyword_rank": result.keyword_rank,
                "metadata": result.metadata,
            }
            for rank, result in enumerate(
                results,
                start=1,
            )
        ]

    def ask_documents(
        self,
        question: str,
        top_k: int = 5,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> dict[str, Any]:
        answer = self.engine.ask(
            question=question,
            top_k=top_k,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )

        return {
            "answer": answer.answer,
            "insufficient_evidence": (
                answer.insufficient_evidence
            ),
            "citations": [
                {
                    "index": citation.index,
                    "chunk_id": citation.chunk_id,
                    "document_id": (
                        citation.document_id
                    ),
                    "source": citation.source,
                    "file_type": citation.file_type,
                    "metadata": citation.metadata,
                }
                for citation in answer.citations
            ],
        }