import pytest

from app.rag.retrieval import SemanticRetriever


class FakeEmbeddingProvider:
    @property
    def dimension(self) -> int:
        return 3

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        return [1.0, 0.0, 0.0]

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            [1.0, 0.0, 0.0]
            for _ in texts
        ]


class FakeVectorStore:
    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[dict]:
        return [
            {
                "chunk_id": "chunk-001",
                "document_id": "doc-001",
                "text": "Remote work is allowed.",
                "source": "remote_work_policy.txt",
                "file_type": "txt",
                "metadata": {
                    "department": "HR"
                },
                "distance": 0.1,
            }
        ][:top_k]


def make_retriever() -> SemanticRetriever:
    return SemanticRetriever(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )


def test_retrieve_returns_ranked_results() -> None:
    retriever = make_retriever()

    results = retriever.retrieve(
        "Can employees work from home?"
    )

    assert len(results) == 1

    result = results[0]

    assert result.chunk_id == "chunk-001"
    assert result.document_id == "doc-001"
    assert (
        result.source
        == "remote_work_policy.txt"
    )
    assert (
        result.text
        == "Remote work is allowed."
    )
    assert result.metadata == {
        "department": "HR"
    }
    assert result.distance == 0.1


def test_retrieve_supports_top_k() -> None:
    retriever = make_retriever()

    results = retriever.retrieve(
        "Remote work",
        top_k=1,
    )

    assert len(results) == 1


def test_empty_query_is_rejected() -> None:
    retriever = make_retriever()

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        retriever.retrieve("   ")


def test_invalid_top_k_is_rejected() -> None:
    retriever = make_retriever()

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        retriever.retrieve(
            "Remote work",
            top_k=0,
        )


def test_retrieve_filters_results_above_max_distance() -> None:
    retriever = make_retriever()

    results = retriever.retrieve(
        "Remote work",
        max_distance=0.05,
    )

    assert results == []


def test_retrieve_keeps_results_within_max_distance() -> None:
    retriever = make_retriever()

    results = retriever.retrieve(
        "Remote work",
        max_distance=0.2,
    )

    assert len(results) == 1
    assert results[0].distance == 0.1


def test_negative_max_distance_is_rejected() -> None:
    retriever = make_retriever()

    with pytest.raises(
        ValueError,
        match="max_distance cannot be negative",
    ):
        retriever.retrieve(
            "Remote work",
            max_distance=-0.1,
        )


def test_document_filter_is_supported() -> None:
    class RecordingVectorStore(
        FakeVectorStore
    ):
        received_filters = None

        def query(
            self,
            vector: list[float],
            top_k: int = 5,
            filters: dict[str, str] | None = None,
        ) -> list[dict]:
            self.received_filters = filters

            return super().query(
                vector,
                top_k,
                filters,
            )

    store = RecordingVectorStore()

    retriever = SemanticRetriever(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=store,
    )

    retriever.retrieve(
        "Remote work",
        document_id="doc-001",
    )

    assert store.received_filters == {
        "document_id": "doc-001"
    }


def test_multiple_filters_are_supported() -> None:
    class RecordingVectorStore(
        FakeVectorStore
    ):
        received_filters = None

        def query(
            self,
            vector: list[float],
            top_k: int = 5,
            filters: dict[str, str] | None = None,
        ) -> list[dict]:
            self.received_filters = filters

            return super().query(
                vector,
                top_k,
                filters,
            )

    store = RecordingVectorStore()

    retriever = SemanticRetriever(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=store,
    )

    retriever.retrieve(
        "Remote work",
        source="policy.pdf",
        file_type=".PDF",
    )

    assert store.received_filters == {
        "source": "policy.pdf",
        "file_type": "pdf",
    }


def test_invalid_file_type_filter_is_rejected() -> None:
    retriever = make_retriever()

    with pytest.raises(
        ValueError,
        match="Unsupported file_type filter",
    ):
        retriever.retrieve(
            "Remote work",
            file_type="csv",
        )


def test_empty_document_filter_is_rejected() -> None:
    retriever = make_retriever()

    with pytest.raises(
        ValueError,
        match="document_id filter cannot be empty",
    ):
        retriever.retrieve(
            "Remote work",
            document_id="   ",
        )


def test_empty_source_filter_is_rejected() -> None:
    retriever = make_retriever()

    with pytest.raises(
        ValueError,
        match="source filter cannot be empty",
    ):
        retriever.retrieve(
            "Remote work",
            source="   ",
        )