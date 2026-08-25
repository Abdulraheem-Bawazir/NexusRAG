from pathlib import Path

import pytest
from docx import Document as DocxDocument

from app.rag.loaders.docx_loader import load_docx


def create_test_docx(
    file_path: Path,
    paragraphs: list[str],
) -> None:
    """Create a small DOCX fixture for loader tests."""

    document = DocxDocument()

    for text in paragraphs:
        document.add_paragraph(text)

    document.save(file_path)


def test_load_docx_extracts_text(tmp_path: Path) -> None:
    file_path = tmp_path / "example.docx"

    create_test_docx(
        file_path,
        [
            "NexusRAG document.",
            "Second paragraph.",
        ],
    )

    document = load_docx(file_path)

    assert document.text == (
        "NexusRAG document.\n\nSecond paragraph."
    )
    assert document.source == "example.docx"
    assert document.file_type == "docx"


def test_load_docx_preserves_paragraph_count(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "example.docx"

    create_test_docx(
        file_path,
        [
            "Paragraph one.",
            "",
            "Paragraph two.",
        ],
    )

    document = load_docx(file_path)

    assert document.metadata["paragraph_count"] == 2


def test_load_docx_contains_source_path(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "example.docx"

    create_test_docx(
        file_path,
        ["NexusRAG document."],
    )

    document = load_docx(file_path)

    assert document.metadata["source_path"] == str(
        file_path.resolve()
    )


def test_load_docx_rejects_missing_file(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.docx"

    with pytest.raises(
        FileNotFoundError,
        match="File not found",
    ):
        load_docx(missing_file)


def test_load_docx_rejects_wrong_extension(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("Not a DOCX.", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=r"Expected a \.docx file",
    ):
        load_docx(file_path)


def test_load_docx_rejects_empty_document(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "empty.docx"

    create_test_docx(
        file_path,
        [
            "",
            "   ",
        ],
    )

    with pytest.raises(
        ValueError,
        match="No extractable text found in DOCX",
    ):
        load_docx(file_path)