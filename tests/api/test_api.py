from pathlib import Path

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_engine
from app.models.citation import SourceCitation
from app.models.document import Document
from app.models.rag_answer import RAGAnswer


class FakeEngine:
    def __init__(self) -> None:
        self.documents = [
            Document(
                id="doc-001",
                text="Remote work is allowed.",
                source="policy.txt",
                file_type="txt",
                metadata={
                    "department": "HR",
                },
            )
        ]

    def ingest_path(
        self,
        path: str | Path,
    ) -> list[Document]:
        return self.documents

    def list_documents(
        self,
    ) -> list[Document]:
        return self.documents

    def delete_document(
        self,
        document_id: str,
    ) -> bool:
        if document_id != "doc-001":
            return False

        self.documents = []

        return True

    def ask(
        self,
        question: str,
        top_k: int = 5,
        max_distance: float | None = None,
        min_keyword_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> RAGAnswer:
        return RAGAnswer(
            answer="Up to three days per week.",
            citations=(
                SourceCitation(
                    index=1,
                    chunk_id="chunk-001",
                    document_id="doc-001",
                    source="policy.txt",
                    file_type="txt",
                    metadata={
                        "department": "HR",
                    },
                ),
            ),
            insufficient_evidence=False,
        )


def create_test_client(
    engine: FakeEngine | None = None,
) -> TestClient:
    app = create_app()

    fake_engine = (
        engine or FakeEngine()
    )

    app.dependency_overrides[
        get_engine
    ] = lambda: fake_engine

    return TestClient(app)


def test_health_endpoint() -> None:
    client = create_test_client()

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "application": "NexusRAG",
    }


def test_query_endpoint() -> None:
    client = create_test_client()

    response = client.post(
        "/api/v1/query",
        json={
            "question": (
                "How many days can employees "
                "work remotely?"
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["answer"]
        == "Up to three days per week."
    )

    assert (
        payload["citations"][0]["source"]
        == "policy.txt"
    )

    assert (
        payload["insufficient_evidence"]
        is False
    )


def test_query_validates_top_k() -> None:
    client = create_test_client()

    response = client.post(
        "/api/v1/query",
        json={
            "question": "Question",
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_list_documents() -> None:
    client = create_test_client()

    response = client.get(
        "/api/v1/documents"
    )

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 1
    assert documents[0]["id"] == "doc-001"


def test_delete_document() -> None:
    client = create_test_client()

    response = client.delete(
        "/api/v1/documents/doc-001"
    )

    assert response.status_code == 204


def test_delete_missing_document_returns_404() -> None:
    client = create_test_client()

    response = client.delete(
        "/api/v1/documents/missing"
    )

    assert response.status_code == 404


def test_upload_txt_document(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "UPLOAD_DIR",
        tmp_path,
    )

    client = create_test_client()

    response = client.post(
        "/api/v1/documents",
        files={
            "file": (
                "policy.txt",
                b"Remote work is allowed.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    payload = response.json()

    assert (
        payload["documents"][0]["id"]
        == "doc-001"
    )


def test_upload_rejects_unsupported_type(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "UPLOAD_DIR",
        tmp_path,
    )

    client = create_test_client()

    response = client.post(
        "/api/v1/documents",
        files={
            "file": (
                "data.csv",
                b"a,b,c",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400


def test_upload_rejects_empty_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "UPLOAD_DIR",
        tmp_path,
    )

    client = create_test_client()

    response = client.post(
        "/api/v1/documents",
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_query_returns_503_when_llm_is_unavailable() -> None:
    class OfflineEngine(FakeEngine):
        def ask(
            self,
            question: str,
            top_k: int = 5,
            max_distance: float | None = None,
            min_keyword_score: float | None = None,
            document_id: str | None = None,
            source: str | None = None,
            file_type: str | None = None,
        ) -> RAGAnswer:
            raise ConnectionError(
                "Ollama offline"
            )

    client = create_test_client(
        OfflineEngine()
    )

    response = client.post(
        "/api/v1/query",
        json={
            "question": "Question"
        },
    )

    assert response.status_code == 503