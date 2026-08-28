from app.rag.embeddings import EmbeddingProvider


class FakeEmbeddingProvider:
    @property
    def dimension(self) -> int:
        return 3

    def embed_text(self, text: str) -> list[float]:
        return [1.0, 2.0, 3.0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 2.0, 3.0] for _ in texts]


def test_fake_provider_matches_embedding_protocol() -> None:
    provider = FakeEmbeddingProvider()

    assert isinstance(provider, EmbeddingProvider)


def test_embedding_provider_dimension() -> None:
    provider = FakeEmbeddingProvider()

    assert provider.dimension == 3


def test_embedding_provider_single_embedding() -> None:
    provider = FakeEmbeddingProvider()

    embedding = provider.embed_text("NexusRAG")

    assert embedding == [1.0, 2.0, 3.0]


def test_embedding_provider_batch_embedding() -> None:
    provider = FakeEmbeddingProvider()

    embeddings = provider.embed_texts(
        [
            "First chunk",
            "Second chunk",
        ]
    )

    assert embeddings == [
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    ]