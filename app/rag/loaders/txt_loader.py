from pathlib import Path
from uuid import uuid4

from app.models.document import Document


def load_txt(file_path: str | Path) -> Document:
    """Load a TXT file and normalize it into a Document."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file, got: {path}")

    if path.suffix.lower() != ".txt":
        raise ValueError(
            f"Expected a .txt file, got: {path.suffix or 'no extension'}"
        )

    text = path.read_text(encoding="utf-8-sig").strip()

    if not text:
        raise ValueError(f"TXT file is empty: {path.name}")

    return Document(
        id=str(uuid4()),
        text=text,
        source=path.name,
        file_type="txt",
        metadata={
            "source_path": str(path.resolve()),
        },
    )