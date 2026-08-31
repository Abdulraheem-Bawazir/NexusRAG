from pathlib import Path

from app.models.document import Document
from app.rag.chunking import DocumentChunker
from app.rag.embeddings import (
    ChunkEmbedder,
    SentenceTransformerEmbeddingProvider,
)
from app.rag.retrieval import (
    HybridRetriever,
    KeywordRetriever,
    NoOpReranker,
    SemanticRetriever,
)
from app.rag.vector_store import ChromaVectorStore


def print_results(
    query: str,
    results: list,
) -> None:
    print(f"\nQuestion: {query}")
    print("Top hybrid matches:")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"\n#{index}")
        print("Source:", result.source)
        print("Text:", result.text)
        print(
            "Hybrid score:",
            round(result.score, 6),
        )
        print(
            "Semantic rank:",
            result.semantic_rank,
        )
        print(
            "Keyword rank:",
            result.keyword_rank,
        )


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
            metadata={"department": "HR"},
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
            metadata={"department": "IT"},
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
            metadata={"department": "HR"},
        ),
        Document(
            id="doc-travel",
            text=(
                "Travel reimbursement policy "
                "TRV-8842 requires employees to "
                "submit receipts within thirty days."
            ),
            source="travel_policy.txt",
            file_type="txt",
            metadata={"department": "Finance"},
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

    persist_directory = Path(
        "data/hybrid_verification"
    )

    vector_store = ChromaVectorStore(
        persist_directory=persist_directory,
        collection_name="hybrid-verification",
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

    semantic_question = (
        "Can employees work from home?"
    )

    semantic_results = (
        hybrid_retriever.retrieve(
            semantic_question,
            top_k=3,
        )
    )

    print_results(
        semantic_question,
        semantic_results,
    )

    assert semantic_results
    assert (
        semantic_results[0].source
        == "remote_work_policy.txt"
    )

    exact_term_question = (
        "What does policy TRV-8842 require?"
    )

    exact_term_results = (
        hybrid_retriever.retrieve(
            exact_term_question,
            top_k=3,
        )
    )

    print_results(
        exact_term_question,
        exact_term_results,
    )

    assert exact_term_results
    assert (
        exact_term_results[0].source
        == "travel_policy.txt"
    )

    assert vector_store.count() == 4

    print(
        "\nHybrid retrieval verification passed."
    )


if __name__ == "__main__":
    main()