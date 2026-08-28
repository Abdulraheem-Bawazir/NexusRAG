from app.rag.chunking import (
    DocumentChunker,
    TextChunker,
    generate_chunk_id,
)


def test_chunking_public_exports() -> None:
    assert DocumentChunker is not None
    assert TextChunker is not None
    assert callable(generate_chunk_id)