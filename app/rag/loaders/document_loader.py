from pathlib import Path

from app.models.document import Document
from app.rag.loaders.docx_loader import load_docx
from app.rag.loaders.pdf_loader import load_pdf
from app.rag.loaders.txt_loader import load_txt

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_document(file_path: str | Path) -> list[Document]:
    """Load a supported document using the appropriate file loader."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension: "
            f"{extension or 'no extension'}. "
            f"Supported extensions: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if extension == ".pdf":
        return load_pdf(path)

    if extension == ".docx":
        return [load_docx(path)]

    return [load_txt(path)]