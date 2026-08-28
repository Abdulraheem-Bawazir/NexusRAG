import hashlib


def generate_chunk_id(
    document_id: str,
    chunk_index: int,
    text: str,
) -> str:
    """Generate a deterministic ID for a document chunk."""

    if not document_id.strip():
        raise ValueError("document_id cannot be empty.")

    if chunk_index < 0:
        raise ValueError("chunk_index cannot be negative.")

    if not text.strip():
        raise ValueError("text cannot be empty.")

    payload = f"{document_id}:{chunk_index}:{text}".encode()

    digest = hashlib.sha256(payload).hexdigest()

    return f"chunk-{digest}"