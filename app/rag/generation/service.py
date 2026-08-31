import json
from typing import Protocol

from app.models.hybrid_retrieval_result import HybridRetrievalResult
from app.models.rag_answer import RAGAnswer
from app.rag.generation.base import LLMProvider
from app.rag.generation.context_builder import ContextBuilder
from app.rag.generation.prompt_builder import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    build_grounded_prompt,
)


class Retriever(Protocol):
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
        ...


class GroundedRAGService:
    """Retrieve evidence and generate a structured grounded answer."""

    def __init__(
        self,
        retriever: Retriever,
        llm_provider: LLMProvider,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm_provider = llm_provider
        self.context_builder = (
            context_builder or ContextBuilder()
        )

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
        if not question.strip():
            raise ValueError(
                "question cannot be empty."
            )

        results = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            max_distance=max_distance,
            min_keyword_score=min_keyword_score,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )

        if not results:
            return RAGAnswer(
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                citations=(),
                insufficient_evidence=True,
            )

        context, available_citations = (
            self.context_builder.build(results)
        )

        if not context:
            return RAGAnswer(
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                citations=(),
                insufficient_evidence=True,
            )

        prompt = build_grounded_prompt(
            question=question,
            context=context,
        )

        raw_response = self.llm_provider.generate(
            prompt
        ).strip()

        if not raw_response:
            raise ValueError(
                "LLM provider returned an empty answer."
            )

        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM provider returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise TypeError(
                "LLM response must be a JSON object."
            )

        answer = payload.get("answer")
        citation_indexes = payload.get("citations")
        insufficient_evidence = payload.get(
            "insufficient_evidence"
        )

        if not isinstance(answer, str):
            raise TypeError(
                "LLM response answer must be a string."
            )

        answer = answer.strip()

        if not answer:
            raise ValueError(
                "LLM provider returned an empty answer."
            )

        if not isinstance(citation_indexes, list):
            raise TypeError(
                "LLM response citations must be a list."
            )

        if any(
            type(index) is not int
            for index in citation_indexes
        ):
            raise TypeError(
                "Citation indexes must be integers."
            )

        if not isinstance(
            insufficient_evidence,
            bool,
        ):
            raise TypeError(
                "insufficient_evidence must be boolean."
            )

        if (
            insufficient_evidence
            or answer
            == INSUFFICIENT_EVIDENCE_MESSAGE
        ):
            return RAGAnswer(
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                citations=(),
                insufficient_evidence=True,
            )

        citations_by_index = {
            citation.index: citation
            for citation in available_citations
        }

        invalid_indexes = [
            index
            for index in citation_indexes
            if index not in citations_by_index
        ]

        if invalid_indexes:
            raise ValueError(
                "LLM cited unavailable source indexes."
            )

        selected_citations = []
        seen_indexes: set[int] = set()

        for index in citation_indexes:
            if index in seen_indexes:
                continue

            seen_indexes.add(index)

            selected_citations.append(
                citations_by_index[index]
            )

        if not selected_citations:
            raise ValueError(
                "Grounded answer must cite at least one source."
            )

        return RAGAnswer(
            answer=answer,
            citations=tuple(selected_citations),
            insufficient_evidence=False,
        )