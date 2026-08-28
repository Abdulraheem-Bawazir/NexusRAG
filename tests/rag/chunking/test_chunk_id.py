import pytest

from app.rag.chunking.chunk_id import generate_chunk_id


def test_chunk_id_is_deterministic() -> None:
    first = generate_chunk_id(
        document_id="doc-001",
        chunk_index=0,
        text="Example chunk text.",
    )

    second = generate_chunk_id(
        document_id="doc-001",
        chunk_index=0,
        text="Example chunk text.",
    )

    assert first == second


def test_chunk_id_changes_when_index_changes() -> None:
    first = generate_chunk_id(
        document_id="doc-001",
        chunk_index=0,
        text="Example chunk text.",
    )

    second = generate_chunk_id(
        document_id="doc-001",
        chunk_index=1,
        text="Example chunk text.",
    )

    assert first != second


def test_chunk_id_changes_when_text_changes() -> None:
    first = generate_chunk_id(
        document_id="doc-001",
        chunk_index=0,
        text="First text.",
    )

    second = generate_chunk_id(
        document_id="doc-001",
        chunk_index=0,
        text="Different text.",
    )

    assert first != second


def test_invalid_chunk_id_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        generate_chunk_id("", 0, "text")

    with pytest.raises(ValueError):
        generate_chunk_id("doc-001", -1, "text")

    with pytest.raises(ValueError):
        generate_chunk_id("doc-001", 0, "   ")