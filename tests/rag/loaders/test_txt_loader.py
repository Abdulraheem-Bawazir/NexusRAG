from pathlib import Path

import pytest

from app.rag.loaders.txt_loader import load_txt


def test_load_txt_returns_document(tmp_path: Path) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text(
        "NexusRAG retrieves useful evidence.",
        encoding="utf-8",
    )

    document = load_txt(file_path)

    assert document.text == "NexusRAG retrieves useful evidence."
    assert document.source == "example.txt"
    assert document.file_type == "txt"
    assert document.id
    assert "source_path" in document.metadata


def test_load_txt_rejects_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError, match="File not found"):
        load_txt(missing_file)


def test_load_txt_rejects_wrong_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "example.pdf"
    file_path.write_text("Not really a PDF.", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Expected a \.txt file"):
        load_txt(file_path)


def test_load_txt_rejects_empty_file(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ", encoding="utf-8")

    with pytest.raises(ValueError, match="TXT file is empty"):
        load_txt(file_path)

def test_load_txt_removes_utf8_bom(tmp_path: Path) -> None:
    file_path = tmp_path / "bom.txt"
    file_path.write_text(
        "\ufeffNexusRAG document.",
        encoding="utf-8",
    )

    document = load_txt(file_path)

    assert document.text == "NexusRAG document."
    assert not document.text.startswith("\ufeff")