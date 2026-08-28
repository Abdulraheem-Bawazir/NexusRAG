import pytest

from app.rag.embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)


class FakeSentenceTransformer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def get_embedding_dimension(self) -> int:
        return 3

    def encode(
        self,
        texts,
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
    ):
        if isinstance(texts, str):
            return [0.1, 0.2, 0.3]

        return [
            [0.1, 0.2, 0.3]
            for _ in texts
        ]


def test_provider_matches_embedding_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.rag.embeddings.sentence_transformer.SentenceTransformer",
        FakeSentenceTransformer,
    )

    provider = SentenceTransformerEmbeddingProvider(
        model_name="fake-model"
    )

    assert isinstance(provider, EmbeddingProvider)


def test_provider_reports_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.rag.embeddings.sentence_transformer.SentenceTransformer",
        FakeSentenceTransformer,
    )

    provider = SentenceTransformerEmbeddingProvider(
        model_name="fake-model"
    )

    assert provider.dimension == 3


def test_provider_embeds_single_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.rag.embeddings.sentence_transformer.SentenceTransformer",
        FakeSentenceTransformer,
    )

    provider = SentenceTransformerEmbeddingProvider(
        model_name="fake-model"
    )

    embedding = provider.embed_text("NexusRAG")

    assert embedding == [0.1, 0.2, 0.3]


def test_provider_embeds_multiple_texts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.rag.embeddings.sentence_transformer.SentenceTransformer",
        FakeSentenceTransformer,
    )

    provider = SentenceTransformerEmbeddingProvider(
        model_name="fake-model"
    )

    embeddings = provider.embed_texts(
        [
            "First chunk",
            "Second chunk",
        ]
    )

    assert embeddings == [
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.3],
    ]


def test_empty_text_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.rag.embeddings.sentence_transformer.SentenceTransformer",
        FakeSentenceTransformer,
    )

    provider = SentenceTransformerEmbeddingProvider(
        model_name="fake-model"
    )

    with pytest.raises(
        ValueError,
        match="text cannot be empty",
    ):
        provider.embed_text("   ")


def test_empty_batch_returns_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.rag.embeddings.sentence_transformer.SentenceTransformer",
        FakeSentenceTransformer,
    )

    provider = SentenceTransformerEmbeddingProvider(
        model_name="fake-model"
    )

    assert provider.embed_texts([]) == []