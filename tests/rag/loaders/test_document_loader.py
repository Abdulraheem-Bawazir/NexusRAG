from pathlib import Path

import pytest
from docx import Document as DocxDocument

from app.rag.loaders.document_loader import load_document
from reportlab.pdfgen import canvas

def test_load_document_routes_txt(tmp_path: Path) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text(
        "NexusRAG TXT document.",
        encoding="utf-8",
    )

    documents = load_document(file_path)

    assert isinstance(documents, list)
    assert len(documents) == 1
    assert documents[0].file_type == "txt"


def test_load_document_routes_docx(tmp_path: Path) -> None:
    file_path = tmp_path / "example.docx"

    docx = DocxDocument()
    docx.add_paragraph("NexusRAG DOCX document.")
    docx.save(file_path)

    documents = load_document(file_path)

    assert isinstance(documents, list)
    assert len(documents) == 1
    assert documents[0].file_type == "docx"


def test_load_document_rejects_unsupported_extension(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "example.csv"
    file_path.write_text(
        "Unsupported file.",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported file extension",
    ):
        load_document(file_path)


def test_load_document_rejects_file_without_extension(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "example"
    file_path.write_text(
        "No extension.",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported file extension",
    ):
        load_document(file_path)

def test_load_document_routes_pdf(tmp_path: Path) -> None:
    file_path = tmp_path / "example.pdf"

    pdf = canvas.Canvas(str(file_path))
    pdf.drawString(72, 750, "NexusRAG PDF document.")
    pdf.save()

    documents = load_document(file_path)

    assert isinstance(documents, list)
    assert len(documents) == 1
    assert documents[0].file_type == "pdf"
    assert "NexusRAG PDF document." in documents[0].text