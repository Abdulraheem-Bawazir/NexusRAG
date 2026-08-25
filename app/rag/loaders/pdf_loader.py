from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from app.models.document import Document


def load_pdf(file_path: str | Path) -> list[Document]:
    """Load a PDF and return one normalized Document per non-empty page."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file, got: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a .pdf file, got: {path.suffix or 'no extension'}"
        )

    reader = PdfReader(path)

    source_id = str(uuid4())
    documents: list[Document] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text is None:
            continue

        text = text.strip()

        if not text:
            continue

        document = Document(
            id=str(uuid4()),
            text=text,
            source=path.name,
            file_type="pdf",
            metadata={
                "source_id": source_id,
                "source_path": str(path.resolve()),
                "page_number": page_number,
                "total_pages": len(reader.pages),
            },
        )

        documents.append(document)

    if not documents:
        raise ValueError(
            f"No extractable text found in PDF: {path.name}"
        )

    return documents