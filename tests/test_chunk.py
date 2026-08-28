import pytest

from app.models.chunk import Chunk


def test_chunk_creation() -> None:
    chunk = Chunk(
        id="chunk-001",
        document_id="doc-001",
        text="This is a test chunk.",
        chunk_index=0,
        source="example.pdf",
        file_type="pdf",
        metadata={"page": 1},
    )

    assert chunk.id == "chunk-001"
    assert chunk.document_id == "doc-001"
    assert chunk.text == "This is a test chunk."
    assert chunk.chunk_index == 0
    assert chunk.source == "example.pdf"
    assert chunk.file_type == "pdf"
    assert chunk.metadata == {"page": 1}


def test_chunk_normalizes_file_type() -> None:
    chunk = Chunk(
        id="chunk-001",
        document_id="doc-001",
        text="Test",
        chunk_index=0,
        source="example.PDF",
        file_type=".PDF",
    )

    assert chunk.file_type == "pdf"


def test_chunk_rejects_empty_text() -> None:
    with pytest.raises(ValueError, match="Chunk text cannot be empty"):
        Chunk(
            id="chunk-001",
            document_id="doc-001",
            text="   ",
            chunk_index=0,
            source="example.pdf",
            file_type="pdf",
        )


def test_chunk_rejects_negative_index() -> None:
    with pytest.raises(ValueError, match="Chunk index cannot be negative"):
        Chunk(
            id="chunk-001",
            document_id="doc-001",
            text="Test",
            chunk_index=-1,
            source="example.pdf",
            file_type="pdf",
        )


def test_chunk_rejects_unsupported_file_type() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        Chunk(
            id="chunk-001",
            document_id="doc-001",
            text="Test",
            chunk_index=0,
            source="example.csv",
            file_type="csv",
        )