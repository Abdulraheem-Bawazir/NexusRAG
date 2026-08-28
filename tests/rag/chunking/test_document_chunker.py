from app.models.document import Document
from app.rag.chunking.document_chunker import DocumentChunker


def test_document_is_converted_into_chunks() -> None:
    document = Document(
        id="doc-001",
        text="ABCDEFGHIJ",
        source="example.pdf",
        file_type="pdf",
    )

    chunker = DocumentChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.chunk_document(document)

    assert len(chunks) == 3

    assert chunks[0].text == "ABCDE"
    assert chunks[1].text == "DEFGH"
    assert chunks[2].text == "GHIJ"


def test_chunks_preserve_document_information() -> None:
    document = Document(
        id="doc-001",
        text="ABCDEFGHIJ",
        source="company_policy.pdf",
        file_type="pdf",
        metadata={
            "page": 4,
            "author": "NexusRAG",
        },
    )

    chunker = DocumentChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.chunk_document(document)

    for chunk in chunks:
        assert chunk.document_id == "doc-001"
        assert chunk.source == "company_policy.pdf"
        assert chunk.file_type == "pdf"
        assert chunk.metadata == {
            "page": 4,
            "author": "NexusRAG",
        }


def test_chunk_indexes_are_sequential() -> None:
    document = Document(
        id="doc-001",
        text="ABCDEFGHIJ",
        source="example.txt",
        file_type="txt",
    )

    chunker = DocumentChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.chunk_document(document)

    assert [chunk.chunk_index for chunk in chunks] == [
        0,
        1,
        2,
    ]


def test_chunk_ids_are_stable() -> None:
    document = Document(
        id="doc-001",
        text="ABCDEFGHIJ",
        source="example.txt",
        file_type="txt",
    )

    chunker = DocumentChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    first_run = chunker.chunk_document(document)
    second_run = chunker.chunk_document(document)

    assert [chunk.id for chunk in first_run] == [
        chunk.id for chunk in second_run
    ]


def test_chunk_metadata_is_copied() -> None:
    document = Document(
        id="doc-001",
        text="ABCDEFGHIJ",
        source="example.pdf",
        file_type="pdf",
        metadata={"page": 1},
    )

    chunker = DocumentChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.chunk_document(document)

    chunks[0].metadata["page"] = 999

    assert document.metadata["page"] == 1

def test_nested_metadata_is_independent() -> None:
    document = Document(
        id="doc-001",
        text="ABCDEFGHIJ",
        source="example.pdf",
        file_type="pdf",
        metadata={
            "location": {
                "page": 1,
                "section": "Introduction",
            }
        },
    )

    chunker = DocumentChunker(
        chunk_size=5,
        chunk_overlap=2,
    )

    chunks = chunker.chunk_document(document)

    chunks[0].metadata["location"]["page"] = 999

    assert document.metadata["location"]["page"] == 1