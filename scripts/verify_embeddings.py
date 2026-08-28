from math import sqrt

from app.rag.embeddings import SentenceTransformerEmbeddingProvider


def vector_norm(vector: list[float]) -> float:
    return sqrt(sum(value * value for value in vector))


def main() -> None:
    provider = SentenceTransformerEmbeddingProvider()

    text = "NexusRAG is a private-document retrieval augmented generation system."

    embedding = provider.embed_text(text)

    print("Model:", provider.model_name)
    print("Dimension:", provider.dimension)
    print("Embedding length:", len(embedding))
    print("First 5 values:", embedding[:5])
    print("Vector norm:", round(vector_norm(embedding), 4))

    assert provider.dimension == 384
    assert len(embedding) == 384

    print("\nReal embedding verification passed.")


if __name__ == "__main__":
    main()