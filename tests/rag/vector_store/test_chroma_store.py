from pathlib import Path

from app.models.chunk import Chunk
from app.models.embedded_chunk import EmbeddedChunk
from app.rag.vector_store import ChromaVectorStore


def make_embedded_chunk(
    chunk_id: str,
    chunk_index: int,
    text: str,
    vector: tuple[float, ...],
) -> EmbeddedChunk:
    chunk = Chunk(
        id=chunk_id,
        document_id="doc-001",
        text=text,
        chunk_index=chunk_index,
        source="example.pdf",
        file_type="pdf",
        metadata={
            "page": chunk_index + 1,
            "section": {
                "name": "Introduction",
            },
        },
    )

    return EmbeddedChunk(
        chunk=chunk,
        vector=vector,
    )


def create_store(tmp_path: Path) -> ChromaVectorStore:
    return ChromaVectorStore(
        persist_directory=tmp_path / "chroma",
        collection_name="test-nexusrag",
    )


def test_upsert_stores_chunks(tmp_path: Path) -> None:
    store = create_store(tmp_path)

    chunks = [
        make_embedded_chunk(
            "chunk-001",
            0,
            "Remote work is allowed.",
            (1.0, 0.0, 0.0),
        ),
        make_embedded_chunk(
            "chunk-002",
            1,
            "Employees receive annual leave.",
            (0.0, 1.0, 0.0),
        ),
    ]

    store.upsert(chunks)

    assert store.count() == 2


def test_upsert_does_not_duplicate_existing_id(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path)

    chunk = make_embedded_chunk(
        "chunk-001",
        0,
        "Remote work is allowed.",
        (1.0, 0.0, 0.0),
    )

    store.upsert([chunk])
    store.upsert([chunk])

    assert store.count() == 1


def test_query_returns_nearest_chunk(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path)

    chunks = [
        make_embedded_chunk(
            "chunk-001",
            0,
            "Remote work is allowed.",
            (1.0, 0.0, 0.0),
        ),
        make_embedded_chunk(
            "chunk-002",
            1,
            "Annual leave policy.",
            (0.0, 1.0, 0.0),
        ),
    ]

    store.upsert(chunks)

    results = store.query(
        vector=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-001"
    assert results[0]["text"] == "Remote work is allowed."


def test_query_preserves_metadata(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path)

    chunk = make_embedded_chunk(
        "chunk-001",
        0,
        "Example policy.",
        (1.0, 0.0, 0.0),
    )

    store.upsert([chunk])

    result = store.query(
        vector=[1.0, 0.0, 0.0],
        top_k=1,
    )[0]

    assert result["document_id"] == "doc-001"
    assert result["source"] == "example.pdf"

    assert result["metadata"] == {
        "page": 1,
        "section": {
            "name": "Introduction",
        },
    }


def test_delete_removes_chunk(tmp_path: Path) -> None:
    store = create_store(tmp_path)

    chunk = make_embedded_chunk(
        "chunk-001",
        0,
        "Example",
        (1.0, 0.0, 0.0),
    )

    store.upsert([chunk])

    assert store.count() == 1

    store.delete(["chunk-001"])

    assert store.count() == 0


def test_empty_query_store_returns_empty_list(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path)

    assert store.query(
        vector=[1.0, 0.0, 0.0],
    ) == []

def test_delete_document_removes_all_document_chunks(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path)

    chunks = [
        make_embedded_chunk(
            "chunk-001",
            0,
            "First chunk",
            (1.0, 0.0, 0.0),
        ),
        make_embedded_chunk(
            "chunk-002",
            1,
            "Second chunk",
            (0.9, 0.1, 0.0),
        ),
    ]

    store.upsert(chunks)

    assert store.count() == 2

    store.delete_document("doc-001")

    assert store.count() == 0


def test_clear_removes_all_chunks(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path)

    chunks = [
        make_embedded_chunk(
            "chunk-001",
            0,
            "First",
            (1.0, 0.0, 0.0),
        ),
        make_embedded_chunk(
            "chunk-002",
            1,
            "Second",
            (0.0, 1.0, 0.0),
        ),
    ]

    store.upsert(chunks)

    assert store.count() == 2

    store.clear()

    assert store.count() == 0


def test_store_data_persists_across_instances(
    tmp_path: Path,
) -> None:
    persist_directory = tmp_path / "persistent-chroma"

    first_store = ChromaVectorStore(
        persist_directory=persist_directory,
        collection_name="persistence-test",
    )

    chunk = make_embedded_chunk(
        "chunk-001",
        0,
        "Persistent information",
        (1.0, 0.0, 0.0),
    )

    first_store.upsert([chunk])

    assert first_store.count() == 1

    second_store = ChromaVectorStore(
        persist_directory=persist_directory,
        collection_name="persistence-test",
    )

    assert second_store.count() == 1

    results = second_store.query(
        vector=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert results[0]["chunk_id"] == "chunk-001"