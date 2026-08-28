import pytest

from app.rag.chunking.text_chunker import TextChunker


def test_split_text_creates_chunks() -> None:
    chunker = TextChunker(
        chunk_size=10,
        chunk_overlap=2,
    )

    chunks = chunker.split_text(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )

    assert chunks == [
        "ABCDEFGHIJ",
        "IJKLMNOPQR",
        "QRSTUVWXYZ",
    ]


def test_split_text_preserves_overlap() -> None:
    chunker = TextChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.split_text("ABCDEFGHIJ")

    assert chunks == [
        "ABCDE",
        "DEFGH",
        "GHIJ",
    ]


def test_short_text_returns_single_chunk() -> None:
    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.split_text("Short document.")

    assert chunks == ["Short document."]


def test_empty_text_returns_no_chunks() -> None:
    chunker = TextChunker()

    assert chunker.split_text("") == []
    assert chunker.split_text("   ") == []


def test_invalid_chunk_size_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="chunk_size must be greater than 0",
    ):
        TextChunker(chunk_size=0)


def test_negative_overlap_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="chunk_overlap cannot be negative",
    ):
        TextChunker(
            chunk_size=100,
            chunk_overlap=-1,
        )


def test_overlap_cannot_equal_chunk_size() -> None:
    with pytest.raises(
        ValueError,
        match="chunk_overlap must be smaller than chunk_size",
    ):
        TextChunker(
            chunk_size=100,
            chunk_overlap=100,
        )

def test_text_exactly_chunk_size_returns_one_chunk() -> None:
    chunker = TextChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    assert chunker.split_text("ABCDE") == ["ABCDE"]


def test_zero_overlap_is_supported() -> None:
    chunker = TextChunker(
        chunk_size=5,
        chunk_overlap=0,
    )

    chunks = chunker.split_text("ABCDEFGHIJ")

    assert chunks == [
        "ABCDE",
        "FGHIJ",
    ]


def test_trailing_chunk_is_not_duplicated() -> None:
    chunker = TextChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.split_text("ABCDEFGH")

    assert chunks == [
        "ABCDE",
        "DEFGH",
    ]