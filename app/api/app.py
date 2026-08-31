from fastapi import FastAPI

from app.api.routes import router
from app.api.schemas import HealthResponse


def create_app() -> FastAPI:
    """Create the NexusRAG FastAPI application."""

    application = FastAPI(
        title="NexusRAG API",
        version="0.1.0",
        description=(
            "Private-document Retrieval-Augmented "
            "Generation API."
        ),
    )

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["system"],
    )
    def health() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            application="NexusRAG",
        )

    application.include_router(
        router,
        prefix="/api/v1",
        tags=["rag"],
    )

    return application