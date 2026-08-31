import logging
import os

from fastapi import FastAPI

from app.api.middleware import (
    RequestLoggingMiddleware,
)
from app.api.routes import router
from app.api.schemas import HealthResponse


def configure_logging() -> None:
    """Configure application logging from environment settings."""

    level_name = os.getenv(
        "NEXUSRAG_LOG_LEVEL",
        "INFO",
    ).upper()

    level = getattr(
        logging,
        level_name,
        logging.INFO,
    )

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


def create_app() -> FastAPI:
    """Create the NexusRAG FastAPI application."""

    configure_logging()

    application = FastAPI(
        title="NexusRAG API",
        version="0.1.0",
        description=(
            "Private-document Retrieval-Augmented "
            "Generation API."
        ),
    )

    application.add_middleware(
        RequestLoggingMiddleware
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