from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Contract for components that convert text into embedding vectors."""

    @property
    def dimension(self) -> int:
        """Return the size of each embedding vector."""
        ...

    def embed_text(self, text: str) -> list[float]:
        """Embed a single piece of text."""
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in one operation."""
        ...