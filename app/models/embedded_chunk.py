from dataclasses import dataclass

from app.models.chunk import Chunk


@dataclass(frozen=True, slots=True)
class EmbeddedChunk:
    """A document chunk paired with its embedding vector."""

    chunk: Chunk
    vector: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.vector:
            raise ValueError("Embedding vector cannot be empty.")