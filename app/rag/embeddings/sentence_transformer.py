from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SentenceTransformerEmbeddingProvider:
    """Local embedding provider backed by Sentence Transformers."""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name cannot be empty.")

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

        dimension = self._model.get_embedding_dimension()
        if dimension is None or dimension <= 0:
            raise ValueError(
                "Embedding model returned an invalid dimension."
            )

        self._dimension = dimension

    @property
    def dimension(self) -> int:
        """Return the embedding vector dimension."""

        return self._dimension

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for one piece of text."""

        if not text.strip():
            raise ValueError("text cannot be empty.")

        embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return [float(value) for value in embedding]

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError(
                "texts cannot contain empty values."
            )

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return [
            [float(value) for value in embedding]
            for embedding in embeddings
        ]