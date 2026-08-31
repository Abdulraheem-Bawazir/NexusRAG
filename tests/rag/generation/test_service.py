import json

import pytest

from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.rag.generation import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    GroundedRAGService,
)


class FakeRetriever:
    def __init__(
        self,
        results: list[HybridRetrievalResult],
    ) -> None:
        self.results = results

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        min_keyword_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[HybridRetrievalResult]:
        return self.results[:top_k]


class FakeLLMProvider:
    def __init__(
        self,
        response: str,
    ) -> None:
        self.response = response
        self.calls = 0
        self.last_prompt = None

    def generate(
        self,
        prompt: str,
    ) -> str:
        self.calls += 1
        self.last_prompt = prompt

        return self.response


def make_result() -> HybridRetrievalResult:
    return HybridRetrievalResult(
        chunk_id="chunk-001",
        document_id="doc-001",
        text=(
            "Employees may work remotely "
            "three days per week."
        ),
        source="remote_policy.txt",
        file_type="txt",
        score=0.5,
        metadata={"department": "HR"},
    )


def structured_response(
    answer: str,
    citations: list[int],
    insufficient_evidence: bool = False,
) -> str:
    return json.dumps(
        {
            "answer": answer,
            "citations": citations,
            "insufficient_evidence": (
                insufficient_evidence
            ),
        }
    )


def test_service_generates_grounded_answer() -> None:
    llm = FakeLLMProvider(
        structured_response(
            (
                "Employees may work remotely "
                "three days per week."
            ),
            [1],
        )
    )

    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=llm,
    )

    answer = service.ask(
        "Can employees work from home?"
    )

    assert not answer.insufficient_evidence

    assert (
        answer.answer
        == "Employees may work remotely "
        "three days per week."
    )

    assert len(answer.citations) == 1

    assert (
        answer.citations[0].source
        == "remote_policy.txt"
    )

    assert llm.calls == 1


def test_service_returns_insufficient_evidence_without_results() -> None:
    llm = FakeLLMProvider(
        "This should never be used."
    )

    service = GroundedRAGService(
        retriever=FakeRetriever([]),
        llm_provider=llm,
    )

    answer = service.ask(
        "Unknown question"
    )

    assert answer.insufficient_evidence

    assert (
        answer.answer
        == INSUFFICIENT_EVIDENCE_MESSAGE
    )

    assert answer.citations == ()
    assert llm.calls == 0


def test_service_accepts_structured_insufficient_evidence() -> None:
    llm = FakeLLMProvider(
        structured_response(
            INSUFFICIENT_EVIDENCE_MESSAGE,
            [],
            insufficient_evidence=True,
        )
    )

    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=llm,
    )

    answer = service.ask(
        "Question"
    )

    assert answer.insufficient_evidence
    assert answer.citations == ()


def test_prompt_contains_retrieved_evidence() -> None:
    llm = FakeLLMProvider(
        structured_response(
            "Answer.",
            [1],
        )
    )

    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=llm,
    )

    service.ask("Remote work?")

    assert llm.last_prompt is not None

    assert (
        "Employees may work remotely"
        in llm.last_prompt
    )


def test_invalid_json_is_rejected() -> None:
    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=FakeLLMProvider(
            "not-json"
        ),
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):
        service.ask(
            "Remote work?"
        )


def test_empty_answer_is_rejected() -> None:
    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=FakeLLMProvider(
            structured_response(
                "   ",
                [1],
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="empty answer",
    ):
        service.ask(
            "Remote work?"
        )


def test_unavailable_citation_is_rejected() -> None:
    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=FakeLLMProvider(
            structured_response(
                "Answer.",
                [99],
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="unavailable source indexes",
    ):
        service.ask(
            "Remote work?"
        )


def test_answer_without_citation_is_rejected() -> None:
    service = GroundedRAGService(
        retriever=FakeRetriever(
            [make_result()]
        ),
        llm_provider=FakeLLMProvider(
            structured_response(
                "Answer.",
                [],
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="must cite at least one source",
    ):
        service.ask(
            "Remote work?"
        )


def test_empty_question_is_rejected() -> None:
    service = GroundedRAGService(
        retriever=FakeRetriever([]),
        llm_provider=FakeLLMProvider(
            "unused"
        ),
    )

    with pytest.raises(
        ValueError,
        match="question cannot be empty",
    ):
        service.ask("   ")