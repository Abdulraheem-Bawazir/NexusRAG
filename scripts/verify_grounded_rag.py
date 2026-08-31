from pathlib import Path

from app.models.document import Document
from app.rag.chunking import DocumentChunker
from app.rag.embeddings import (
    ChunkEmbedder,
    SentenceTransformerEmbeddingProvider,
)
from app.rag.generation import (
    GroundedRAGService,
    OllamaLLMProvider,
)
from app.rag.retrieval import (
    HybridRetriever,
    KeywordRetriever,
    NoOpReranker,
    SemanticRetriever,
)
from app.rag.vector_store import ChromaVectorStore


def main() -> None:
    documents = [
        Document(
            id="doc-remote",
            text=(
                "Employees may work remotely up to "
                "three days per week. Remote work "
                "must be approved by the employee's "
                "manager."
            ),
            source="remote_work_policy.txt",
            file_type="txt",
            metadata={
                "department": "HR",
            },
        ),
        Document(
            id="doc-leave",
            text=(
                "Full-time employees receive "
                "twenty-five days of paid annual "
                "leave each year."
            ),
            source="annual_leave_policy.txt",
            file_type="txt",
            metadata={
                "department": "HR",
            },
        ),
        Document(
            id="doc-security",
            text=(
                "Employees must use multi-factor "
                "authentication and must never share "
                "company passwords."
            ),
            source="security_policy.txt",
            file_type="txt",
            metadata={
                "department": "IT",
            },
        ),
    ]

    chunker = DocumentChunker(
        chunk_size=250,
        chunk_overlap=30,
    )

    chunks = []

    for document in documents:
        chunks.extend(
            chunker.chunk_document(document)
        )

    embedding_provider = (
        SentenceTransformerEmbeddingProvider()
    )

    chunk_embedder = ChunkEmbedder(
        embedding_provider
    )

    embedded_chunks = (
        chunk_embedder.embed_chunks(chunks)
    )

    vector_store = ChromaVectorStore(
        persist_directory=Path(
            "data/grounded_rag_verification"
        ),
        collection_name="grounded-rag-verification",
    )

    vector_store.upsert(embedded_chunks)

    semantic_retriever = SemanticRetriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    keyword_retriever = KeywordRetriever(
        chunks=chunks
    )

    hybrid_retriever = HybridRetriever(
        semantic_retriever=semantic_retriever,
        keyword_retriever=keyword_retriever,
        reranker=NoOpReranker(),
    )

    llm_provider = OllamaLLMProvider(
        model="qwen3:4b"
    )

    rag = GroundedRAGService(
        retriever=hybrid_retriever,
        llm_provider=llm_provider,
    )

    question = (
        "How many days per week can employees "
        "work from home?"
    )

    answer = rag.ask(
        question=question,
        top_k=3,
    )

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer.answer)

    print("\nCitations:")

    for citation in answer.citations:
        print(
            f"[{citation.index}] "
            f"{citation.source} "
            f"{citation.metadata}"
        )

    assert not answer.insufficient_evidence
    assert answer.citations

    assert any(
        citation.source
        == "remote_work_policy.txt"
        for citation in answer.citations
    )

    print(
        "\nGrounded RAG verification passed."
    )


if __name__ == "__main__":
    main()