from app.mcp.tools import MCPToolService
from app.models.citation import SourceCitation
from app.models.document import Document
from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.models.rag_answer import RAGAnswer


class FakeEngine:
    def list_documents(
        self,
    ) -> list[Document]:
        return [
            Document(
                id="doc-001",
                text="Remote work policy.",
                source="policy.txt",
                file_type="txt",
                metadata={
                    "department": "HR",
                },
            )
        ]

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        min_keyword_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[HybridRetrievalResult]:
        return [
            HybridRetrievalResult(
                chunk_id="chunk-001",
                document_id="doc-001",
                text=(
                    "Employees may work remotely "
                    "three days per week."
                ),
                source="policy.txt",
                file_type="txt",
                score=0.5,
                semantic_rank=1,
                keyword_rank=1,
                metadata={
                    "department": "HR",
                },
            )
        ][:top_k]

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
            answer=(
                "Employees may work remotely "
                "up to three days per week."
            ),
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
        )


def test_list_documents_tool_service() -> None:
    service = MCPToolService(
        FakeEngine()
    )

    documents = service.list_documents()

    assert len(documents) == 1

    assert (
        documents[0]["source"]
        == "policy.txt"
    )


def test_search_documents_returns_ranked_evidence() -> None:
    service = MCPToolService(
        FakeEngine()
    )

    results = service.search_documents(
        "remote work",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["rank"] == 1
    assert (
        results[0]["chunk_id"]
        == "chunk-001"
    )
    assert (
        results[0]["source"]
        == "policy.txt"
    )


def test_search_documents_preserves_metadata() -> None:
    service = MCPToolService(
        FakeEngine()
    )

    results = service.search_documents(
        "remote work"
    )

    assert results[0]["metadata"] == {
        "department": "HR"
    }


def test_ask_documents_returns_answer_and_citations() -> None:
    service = MCPToolService(
        FakeEngine()
    )

    result = service.ask_documents(
        "Can employees work remotely?"
    )

    assert (
        result["answer"]
        == "Employees may work remotely "
        "up to three days per week."
    )

    assert (
        result["insufficient_evidence"]
        is False
    )

    assert (
        result["citations"][0]["source"]
        == "policy.txt"
    )