from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    application: str


class CitationResponse(BaseModel):
    index: int
    chunk_id: str
    document_id: str
    source: str
    file_type: str
    metadata: dict[str, Any]


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )
    max_distance: float | None = Field(
        default=None,
        ge=0,
    )
    min_keyword_score: float | None = None
    document_id: str | None = None
    source: str | None = None
    file_type: str | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    insufficient_evidence: bool


class DocumentResponse(BaseModel):
    id: str
    source: str
    file_type: str
    metadata: dict[str, Any]


class DocumentUploadResponse(BaseModel):
    documents: list[DocumentResponse]