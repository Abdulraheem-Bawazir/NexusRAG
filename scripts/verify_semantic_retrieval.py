from pathlib import Path

from app.models.document import Document
from app.rag.chunking import DocumentChunker
from app.rag.embeddings import (
    ChunkEmbedder,
    SentenceTransformerEmbeddingProvider,
)
from app.rag.vector_store import ChromaVectorStore


def main() -> None:
    documents = [
        Document(
            id="doc-remote-work",
            text=(
                "Employees may work remotely up to three days per week. "
                "Remote work must be approved by the employee's manager."
            ),
            source="remote_work_policy.txt",
            file_type="txt",
            metadata={"department": "HR"},
        ),
        Document(
            id="doc-annual-leave",
            text=(
                "Full-time employees receive twenty-five days of "
                "paid annual leave each year."
            ),
            source="annual_leave_policy.txt",
            file_type="txt",
            metadata={"department": "HR"},
        ),
        Document(
            id="doc-security",
            text=(
                "Employees must use multi-factor authentication and "
                "must never share company passwords."
            ),
            source="security_policy.txt",
            file_type="txt",
            metadata={"department": "IT"},
        ),
    ]

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=20,
    )

    chunks = []

    for document in documents:
        chunks.extend(
            chunker.chunk_document(document)
        )

    provider = SentenceTransformerEmbeddingProvider()

    embedder = ChunkEmbedder(provider)

    embedded_chunks = embedder.embed_chunks(chunks)

    verification_directory = Path(
        "data/semantic_verification"
    )

    store = ChromaVectorStore(
        persist_directory=verification_directory,
        collection_name="semantic-verification",
    )

    store.upsert(embedded_chunks)

    question = "Can employees work from home?"

    query_vector = provider.embed_text(question)

    results = store.query(
        vector=query_vector,
        top_k=2,
    )

    print(f"\nQuestion: {question}")
    print(f"Indexed chunks: {store.count()}")
    print("\nTop matches:")

    for index, result in enumerate(results, start=1):
        print(f"\n#{index}")
        print("Source:", result["source"])
        print("Text:", result["text"])
        print(
            "Distance:",
            round(result["distance"], 4),
        )

    assert results
    assert (
        results[0]["source"]
        == "remote_work_policy.txt"
    )

    print(
        "\nSemantic retrieval verification passed."
    )


if __name__ == "__main__":
    main()