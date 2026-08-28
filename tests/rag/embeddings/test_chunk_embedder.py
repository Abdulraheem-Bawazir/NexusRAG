import pytest

from app.models.chunk import Chunk
from app.rag.embeddings.chunk_embedder import ChunkEmbedder


class FakeEmbeddingProvider:
    @property
    def dimension(self) -> int:
        return 3

    def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            [0.1, 0.2, 0.3]
            for _ in texts
        ]


def make_chunk(
    chunk_id: str,
    index: int,
    text: str,
) -> Chunk:
    return Chunk(
        id=chunk_id,
        document_id="doc-001",
        text=text,
        chunk_index=index,
        source="example.pdf",
        file_type="pdf",
        metadata={"page": 1},
    )


def test_embed_chunks_returns_embedded_chunks() -> None:
    provider = FakeEmbeddingProvider()
    embedder = ChunkEmbedder(provider)

    chunks = [
        make_chunk("chunk-001", 0, "First chunk"),
        make_chunk("chunk-002", 1, "Second chunk"),
    ]

    results = embedder.embed_chunks(chunks)

    assert len(results) == 2

    assert results[0].chunk == chunks[0]
    assert results[1].chunk == chunks[1]

    assert results[0].vector == (0.1, 0.2, 0.3)
    assert results[1].vector == (0.1, 0.2, 0.3)


def test_embed_chunks_preserves_chunk_metadata() -> None:
    provider = FakeEmbeddingProvider()
    embedder = ChunkEmbedder(provider)

    chunk = make_chunk(
        "chunk-001",
        0,
        "Example text",
    )

    result = embedder.embed_chunks([chunk])[0]

    assert result.chunk.document_id == "doc-001"
    assert result.chunk.source == "example.pdf"
    assert result.chunk.metadata == {"page": 1}


def test_empty_chunk_list_returns_empty_list() -> None:
    provider = FakeEmbeddingProvider()
    embedder = ChunkEmbedder(provider)

    assert embedder.embed_chunks([]) == []


def test_wrong_vector_count_is_rejected() -> None:
    class BrokenProvider(FakeEmbeddingProvider):
        def embed_texts(
            self,
            texts: list[str],
        ) -> list[list[float]]:
            return []

    embedder = ChunkEmbedder(BrokenProvider())

    chunks = [
        make_chunk(
            "chunk-001",
            0,
            "Example",
        )
    ]

    with pytest.raises(
        ValueError,
        match="unexpected number of vectors",
    ):
        embedder.embed_chunks(chunks)


def test_wrong_vector_dimension_is_rejected() -> None:
    class BrokenProvider(FakeEmbeddingProvider):
        def embed_texts(
            self,
            texts: list[str],
        ) -> list[list[float]]:
            return [
                [0.1, 0.2]
                for _ in texts
            ]

    embedder = ChunkEmbedder(BrokenProvider())

    chunks = [
        make_chunk(
            "chunk-001",
            0,
            "Example",
        )
    ]

    with pytest.raises(
        ValueError,
        match="dimension does not match",
    ):
        embedder.embed_chunks(chunks)