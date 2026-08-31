from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from app.api.dependencies import get_engine
from app.api.schemas import (
    CitationResponse,
    DocumentResponse,
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
)
from app.models.document import Document
from app.services import NexusRAGEngine

router = APIRouter()

UPLOAD_DIR = Path("data/raw")

SUPPORTED_UPLOAD_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}

EngineDependency = Annotated[
    NexusRAGEngine,
    Depends(get_engine),
]

UploadFileDependency = Annotated[
    UploadFile,
    File(),
]


def document_to_response(
    document: Document,
) -> DocumentResponse:
    """Convert an internal document into an API response."""

    return DocumentResponse(
        id=document.id,
        source=document.source,
        file_type=document.file_type,
        metadata=document.metadata,
    )


def source_group_key(
    document: Document,
) -> str:
    """Return one stable key for all pages of a source file."""

    source_id = document.metadata.get(
        "source_id"
    )

    if source_id is not None:
        return str(source_id)

    return document.id


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFileDependency,
    engine: EngineDependency,
) -> DocumentUploadResponse:
    """Upload, ingest, embed, and index one supported document."""

    filename = Path(
        file.filename or ""
    ).name

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    suffix = Path(filename).suffix.lower()

    if suffix not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document type.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file cannot be empty.",
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = UPLOAD_DIR / filename

    destination.write_bytes(
        content
    )

    try:
        documents = engine.ingest_path(
            destination
        )
    except Exception as exc:
        destination.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    displayed_documents: list[Document] = []
    seen_sources: set[str] = set()

    for document in documents:
        group_key = source_group_key(
            document
        )

        if group_key in seen_sources:
            continue

        seen_sources.add(
            group_key
        )

        displayed_documents.append(
            document
        )

    return DocumentUploadResponse(
        documents=[
            document_to_response(document)
            for document
            in displayed_documents
        ]
    )


@router.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    engine: EngineDependency,
) -> list[DocumentResponse]:
    """List uploaded source files instead of individual PDF pages."""

    responses: list[DocumentResponse] = []
    seen_sources: set[str] = set()

    for document in engine.list_documents():
        group_key = source_group_key(
            document
        )

        if group_key in seen_sources:
            continue

        seen_sources.add(
            group_key
        )

        responses.append(
            document_to_response(
                document
            )
        )

    return responses


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: str,
    engine: EngineDependency,
) -> Response:
    """Delete one uploaded source and all its page documents."""

    deleted = engine.delete_document(
        document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query_documents(
    request: QueryRequest,
    engine: EngineDependency,
) -> QueryResponse:
    """Run a grounded RAG query against indexed documents."""

    try:
        result = engine.ask(
            question=request.question,
            top_k=request.top_k,
            max_distance=request.max_distance,
            min_keyword_score=(
                request.min_keyword_score
            ),
            document_id=request.document_id,
            source=request.source,
            file_type=request.file_type,
        )

    except (ConnectionError, TimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Local LLM service is unavailable.",
        ) from exc

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    citations = [
        CitationResponse(
            index=citation.index,
            chunk_id=citation.chunk_id,
            document_id=citation.document_id,
            source=citation.source,
            file_type=citation.file_type,
            metadata=citation.metadata,
        )
        for citation in result.citations
    ]

    return QueryResponse(
        answer=result.answer,
        citations=citations,
        insufficient_evidence=(
            result.insufficient_evidence
        ),
    )