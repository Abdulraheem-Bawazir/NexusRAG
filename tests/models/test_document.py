import pytest

from app.models.document import Document


def test_document_creation() -> None:
    document = Document(
        id="doc-001",
        text="NexusRAG retrieves relevant information.",
        source="example.txt",
        file_type="txt",
        metadata={"author": "NexusRAG"},
    )

    assert document.id == "doc-001"
    assert document.text == "NexusRAG retrieves relevant information."
    assert document.source == "example.txt"
    assert document.file_type == "txt"
    assert document.metadata["author"] == "NexusRAG"


def test_file_type_is_normalized() -> None:
    document = Document(
        id="doc-002",
        text="Example document.",
        source="example.PDF",
        file_type="PDF",
    )

    assert document.file_type == "pdf"


def test_empty_text_is_rejected() -> None:
    with pytest.raises(ValueError, match="Document text cannot be empty"):
        Document(
            id="doc-003",
            text="   ",
            source="empty.txt",
            file_type="txt",
        )


def test_unsupported_file_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        Document(
            id="doc-004",
            text="Some text.",
            source="example.csv",
            file_type="csv",
        )