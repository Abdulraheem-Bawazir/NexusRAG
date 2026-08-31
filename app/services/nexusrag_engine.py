from pathlib import Path

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.models.rag_answer import RAGAnswer
from app.rag.chunking import DocumentChunker
from app.rag.embeddings import (
    ChunkEmbedder,
    EmbeddingProvider,
)
from app.rag.generation import (
    GroundedRAGService,
    LLMProvider,
)
from app.rag.loaders.document_loader import load_document
from app.rag.retrieval import (
    HybridRetriever,
    KeywordRetriever,
    NoOpReranker,
    SemanticRetriever,
)
from app.rag.vector_store import ChromaVectorStore


class NexusRAGEngine:
    """Coordinate ingestion, retrieval, and grounded generation."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
        llm_provider: LLMProvider,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.chunker = chunker or DocumentChunker()

        self.chunk_embedder = ChunkEmbedder(
            embedding_provider
        )

        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, Chunk] = {}

        self._refresh_retrieval()

    def _refresh_retrieval(self) -> None:
        semantic_retriever = SemanticRetriever(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )

        keyword_retriever = KeywordRetriever(
            chunks=list(self._chunks.values())
        )

        self.hybrid_retriever = HybridRetriever(
            semantic_retriever=semantic_retriever,
            keyword_retriever=keyword_retriever,
            reranker=NoOpReranker(),
        )

        self.rag_service = GroundedRAGService(
            retriever=self.hybrid_retriever,
            llm_provider=self.llm_provider,
        )

    def ingest_path(
        self,
        path: str | Path,
    ) -> list[Document]:
        """Parse, chunk, embed, and index one file."""

        documents = load_document(path)

        chunks: list[Chunk] = []

        for document in documents:
            chunks.extend(
                self.chunker.chunk_document(
                    document
                )
            )

        embedded_chunks = (
            self.chunk_embedder.embed_chunks(
                chunks
            )
        )

        self.vector_store.upsert(
            embedded_chunks
        )

        for document in documents:
            self._documents[
                document.id
            ] = document

        for chunk in chunks:
            self._chunks[
                chunk.id
            ] = chunk

        self._refresh_retrieval()

        return documents

    def list_documents(
        self,
    ) -> list[Document]:
        """Return internal page-aware documents."""

        return list(
            self._documents.values()
        )

    def delete_document(
        self,
        document_id: str,
    ) -> bool:
        """Delete a document or all pages belonging to its source."""

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        target = self._documents.get(
            document_id
        )

        if target is None:
            return False

        source_id = target.metadata.get(
            "source_id"
        )

        if source_id is None:
            document_ids = {
                document_id
            }
        else:
            document_ids = {
                document.id
                for document
                in self._documents.values()
                if document.metadata.get(
                    "source_id"
                )
                == source_id
            }

        for current_id in document_ids:
            self.vector_store.delete_document(
                current_id
            )

            self._documents.pop(
                current_id,
                None,
            )

        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk
            in self._chunks.items()
            if chunk.document_id
            not in document_ids
        }

        self._refresh_retrieval()

        return True

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
        """Search indexed evidence without invoking the LLM."""

        return self.hybrid_retriever.retrieve(
            query=query,
            top_k=top_k,
            max_distance=max_distance,
            min_keyword_score=min_keyword_score,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )

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
        """Run the grounded RAG pipeline."""

        return self.rag_service.ask(
            question=question,
            top_k=top_k,
            max_distance=max_distance,
            min_keyword_score=min_keyword_score,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )