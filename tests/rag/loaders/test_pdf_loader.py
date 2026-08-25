from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from app.rag.loaders.pdf_loader import load_pdf


def create_test_pdf(
    file_path: Path,
    pages: list[str | None],
) -> None:
    """Create a small PDF fixture for loader tests."""

    pdf = canvas.Canvas(str(file_path))

    for text in pages:
        if text:
            pdf.drawString(72, 750, text)

        pdf.showPage()

    pdf.save()


def test_load_pdf_extracts_pages(tmp_path: Path) -> None:
    file_path = tmp_path / "example.pdf"

    create_test_pdf(
        file_path,
        [
            "NexusRAG page one.",
            "NexusRAG page two.",
        ],
    )

    documents = load_pdf(file_path)

    assert len(documents) == 2

    assert "NexusRAG page one." in documents[0].text
    assert "NexusRAG page two." in documents[1].text

    assert documents[0].file_type == "pdf"
    assert documents[0].source == "example.pdf"


def test_load_pdf_preserves_page_numbers(tmp_path: Path) -> None:
    file_path = tmp_path / "example.pdf"

    create_test_pdf(
        file_path,
        [
            "First page.",
            None,
            "Third page.",
        ],
    )

    documents = load_pdf(file_path)

    assert len(documents) == 2

    assert documents[0].metadata["page_number"] == 1
    assert documents[1].metadata["page_number"] == 3

    assert documents[0].metadata["total_pages"] == 3
    assert documents[1].metadata["total_pages"] == 3


def test_pdf_pages_share_source_id(tmp_path: Path) -> None:
    file_path = tmp_path / "example.pdf"

    create_test_pdf(
        file_path,
        [
            "Page one.",
            "Page two.",
        ],
    )

    documents = load_pdf(file_path)

    assert (
        documents[0].metadata["source_id"]
        == documents[1].metadata["source_id"]
    )

    assert documents[0].id != documents[1].id


def test_load_pdf_rejects_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError, match="File not found"):
        load_pdf(missing_file)


def test_load_pdf_rejects_wrong_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("Not a PDF.", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Expected a \.pdf file"):
        load_pdf(file_path)


def test_load_pdf_rejects_pdf_without_text(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.pdf"

    create_test_pdf(
        file_path,
        [
            None,
            None,
        ],
    )

    with pytest.raises(
        ValueError,
        match="No extractable text found in PDF",
    ):
        load_pdf(file_path)