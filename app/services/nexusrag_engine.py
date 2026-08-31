from pathlib import Path

from app.models.chunk import Chunk
from app.models.document import Document
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
    """Application service coordinating ingestion, retrieval, and generation."""

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

        hybrid_retriever = HybridRetriever(
            semantic_retriever=semantic_retriever,
            keyword_retriever=keyword_retriever,
            reranker=NoOpReranker(),
        )

        self.rag_service = GroundedRAGService(
            retriever=hybrid_retriever,
            llm_provider=self.llm_provider,
        )

    def ingest_path(
        self,
        path: str | Path,
    ) -> list[Document]:
        """Parse, chunk, embed, and index one uploaded file."""

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
            self._documents[document.id] = document

        for chunk in chunks:
            self._chunks[chunk.id] = chunk

        self._refresh_retrieval()

        return documents

    def list_documents(
        self,
    ) -> list[Document]:
        """Return documents indexed during this application process."""

        return list(
            self._documents.values()
        )

    def delete_document(
        self,
        document_id: str,
    ) -> bool:
        """Delete one document and its indexed chunks."""

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        document = self._documents.pop(
            document_id,
            None,
        )

        if document is None:
            return False

        self.vector_store.delete_document(
            document_id
        )

        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self._chunks.items()
            if chunk.document_id != document_id
        }

        self._refresh_retrieval()

        return True

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