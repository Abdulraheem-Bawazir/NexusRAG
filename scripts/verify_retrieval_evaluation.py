from pathlib import Path

from app.evaluation import (
    RetrievalEvaluationCase,
    evaluate_retrieval,
)
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


def main() -> None:
    documents = [
        Document(
            id="doc-remote",
            text=(
                "Employees may work remotely up to "
                "three days per week."
            ),
            source="remote_work_policy.txt",
            file_type="txt",
        ),
        Document(
            id="doc-leave",
            text=(
                "Full-time employees receive "
                "twenty-five days of annual leave."
            ),
            source="annual_leave_policy.txt",
            file_type="txt",
        ),
        Document(
            id="doc-security",
            text=(
                "Employees must use multi-factor "
                "authentication for company systems."
            ),
            source="security_policy.txt",
            file_type="txt",
        ),
        Document(
            id="doc-travel",
            text=(
                "Policy TRV-8842 requires travel "
                "receipts within thirty days."
            ),
            source="travel_policy.txt",
            file_type="txt",
        ),
    ]

    chunker = DocumentChunker(
        chunk_size=250,
        chunk_overlap=30,
    )

    chunks = []

    for document in documents:
        chunks.extend(
            chunker.chunk_document(
                document
            )
        )

    chunks_by_document = {
        chunk.document_id: chunk.id
        for chunk in chunks
    }

    cases = [
        RetrievalEvaluationCase(
            query="Can employees work from home?",
            expected_chunk_ids=frozenset(
                {
                    chunks_by_document[
                        "doc-remote"
                    ]
                }
            ),
        ),
        RetrievalEvaluationCase(
            query="How much annual leave do employees receive?",
            expected_chunk_ids=frozenset(
                {
                    chunks_by_document[
                        "doc-leave"
                    ]
                }
            ),
        ),
        RetrievalEvaluationCase(
            query="What authentication method is required?",
            expected_chunk_ids=frozenset(
                {
                    chunks_by_document[
                        "doc-security"
                    ]
                }
            ),
        ),
        RetrievalEvaluationCase(
            query="What does TRV-8842 require?",
            expected_chunk_ids=frozenset(
                {
                    chunks_by_document[
                        "doc-travel"
                    ]
                }
            ),
        ),
    ]

    embedding_provider = (
        SentenceTransformerEmbeddingProvider()
    )

    embedded_chunks = ChunkEmbedder(
        embedding_provider
    ).embed_chunks(
        chunks
    )

    vector_store = ChromaVectorStore(
        persist_directory=Path(
            "data/evaluation_verification"
        ),
        collection_name=(
            "retrieval-evaluation"
        ),
    )

    vector_store.upsert(
        embedded_chunks
    )

    semantic_retriever = SemanticRetriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    keyword_retriever = KeywordRetriever(
        chunks=chunks
    )

    retriever = HybridRetriever(
        semantic_retriever=semantic_retriever,
        keyword_retriever=keyword_retriever,
        reranker=NoOpReranker(),
    )

    rankings: dict[
        str,
        list[str],
    ] = {}

    for case in cases:
        results = retriever.retrieve(
            case.query,
            top_k=3,
        )

        rankings[case.query] = [
            result.chunk_id
            for result in results
        ]

        print(
            f"\nQuery: {case.query}"
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{result.source}"
            )

    metrics = evaluate_retrieval(
        cases=cases,
        ranked_results=rankings,
        k=3,
    )

    print("\nRetrieval Evaluation")
    print(
        "Cases:",
        metrics.case_count,
    )
    print(
        "Hit Rate@3:",
        round(
            metrics.hit_rate_at_k,
            4,
        ),
    )
    print(
        "Recall@3:",
        round(
            metrics.recall_at_k,
            4,
        ),
    )
    print(
        "MRR:",
        round(
            metrics.mrr,
            4,
        ),
    )

    assert metrics.hit_rate_at_k >= 0.75

    print(
        "\nRetrieval evaluation verification passed."
    )


if __name__ == "__main__":
    main()