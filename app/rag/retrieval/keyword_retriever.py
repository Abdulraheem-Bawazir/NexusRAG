import re

from rank_bm25 import BM25Okapi

from app.models.chunk import Chunk
from app.models.keyword_retrieval_result import KeywordRetrievalResult


def tokenize(text: str) -> list[str]:
    """Normalize text into lowercase keyword tokens."""

    return re.findall(
        r"\b\w+\b",
        text.lower(),
        flags=re.UNICODE,
    )


class KeywordRetriever:
    """BM25 keyword retriever for indexed chunks."""

    def __init__(
        self,
        chunks: list[Chunk],
    ) -> None:
        self.chunks = list(chunks)

        self._tokenized_corpus = [
            tokenize(chunk.text)
            for chunk in self.chunks
        ]

        self._bm25 = (
            BM25Okapi(self._tokenized_corpus)
            if self._tokenized_corpus
            else None
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        document_id: str | None = None,
        source: str | None = None,
        file_type: str | None = None,
    ) -> list[KeywordRetrievalResult]:
        """Return chunks ranked by BM25 keyword relevance."""

        if not query.strip():
            raise ValueError("query cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        if not self.chunks or self._bm25 is None:
            return []

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        scores = self._bm25.get_scores(
            query_tokens
        )

        ranked = sorted(
            zip(
                self.chunks,
                scores,
                strict=True,
            ),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        results: list[KeywordRetrievalResult] = []

        for chunk, score_value in ranked:
            score = float(score_value)

            if (
                min_score is not None
                and score < min_score
            ):
                continue

            if (
                document_id is not None
                and chunk.document_id
                != document_id
            ):
                continue

            if (
                source is not None
                and chunk.source != source
            ):
                continue

            if (
                file_type is not None
                and chunk.file_type
                != file_type.lower().lstrip(".")
            ):
                continue

            results.append(
                KeywordRetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    source=chunk.source,
                    file_type=chunk.file_type,
                    score=score,
                    metadata=dict(chunk.metadata),
                )
            )

            if len(results) >= top_k:
                break

        return results