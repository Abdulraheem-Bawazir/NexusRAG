from app.models.chunk import Chunk
from app.models.embedded_chunk import EmbeddedChunk
from app.rag.embeddings.base import EmbeddingProvider


class ChunkEmbedder:
    """Generate validated embeddings for retrieval-ready chunks."""

    def __init__(self, provider: EmbeddingProvider) -> None:
        self.provider = provider

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:
        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]

        vectors = self.provider.embed_texts(texts)

        if len(vectors) != len(chunks):
            raise ValueError(
                "Embedding provider returned an unexpected number of vectors."
            )

        embedded_chunks: list[EmbeddedChunk] = []

        for chunk, vector in zip(chunks, vectors, strict=True):
            if len(vector) != self.provider.dimension:
                raise ValueError(
                    "Embedding vector dimension does not match provider dimension."
                )

            embedded_chunks.append(
                EmbeddedChunk(
                    chunk=chunk,
                    vector=tuple(vector),
                )
            )

        return embedded_chunks