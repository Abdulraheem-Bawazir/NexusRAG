import os
from functools import lru_cache
from pathlib import Path

from app.rag.embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from app.rag.generation import OllamaLLMProvider
from app.rag.vector_store import ChromaVectorStore
from app.services import NexusRAGEngine

DEFAULT_VECTOR_STORE_DIRECTORY = (
    "data/vector_store"
)


@lru_cache
def get_engine() -> NexusRAGEngine:
    """Create the application-level NexusRAG engine once."""

    embedding_provider = (
        SentenceTransformerEmbeddingProvider()
    )

    vector_store_directory = Path(
        os.getenv(
            "NEXUSRAG_VECTOR_STORE_DIR",
            DEFAULT_VECTOR_STORE_DIRECTORY,
        )
    )

    vector_store = ChromaVectorStore(
        persist_directory=vector_store_directory,
        collection_name="nexusrag-documents",
    )

    llm_model = os.getenv(
        "NEXUSRAG_OLLAMA_MODEL",
        "qwen3:4b",
    )

    llm_base_url = os.getenv(
        "NEXUSRAG_OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    llm_timeout = float(
        os.getenv(
            "NEXUSRAG_OLLAMA_TIMEOUT",
            "300",
        )
    )

    llm_provider = OllamaLLMProvider(
        model=llm_model,
        base_url=llm_base_url,
        timeout=llm_timeout,
    )

    return NexusRAGEngine(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        llm_provider=llm_provider,
    )