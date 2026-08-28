from copy import deepcopy

from app.models.chunk import Chunk
from app.models.document import Document
from app.rag.chunking.chunk_id import generate_chunk_id
from app.rag.chunking.text_chunker import TextChunker


class DocumentChunker:
    """Convert normalized documents into retrieval-ready chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        self.text_chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Split a document into Chunk objects."""

        text_chunks = self.text_chunker.split_text(document.text)

        chunks: list[Chunk] = []

        for index, text in enumerate(text_chunks):
            chunk_id = generate_chunk_id(
                document_id=document.id,
                chunk_index=index,
                text=text,
            )

            chunk = Chunk(
                id=chunk_id,
                document_id=document.id,
                text=text,
                chunk_index=index,
                source=document.source,
                file_type=document.file_type,
                metadata=deepcopy(document.metadata),
            )

            chunks.append(chunk)

        return chunks