from functools import lru_cache
from pathlib import Path

from app.rag.embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from app.rag.generation import OllamaLLMProvider
from app.rag.vector_store import ChromaVectorStore
from app.services import NexusRAGEngine


@lru_cache
def get_engine() -> NexusRAGEngine:
    """Create the application-level NexusRAG engine once."""

    embedding_provider = (
        SentenceTransformerEmbeddingProvider()
    )

    vector_store = ChromaVectorStore(
        persist_directory=Path(
            "data/vector_store"
        ),
        collection_name="nexusrag-documents",
    )

    llm_provider = OllamaLLMProvider()

    return NexusRAGEngine(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        llm_provider=llm_provider,
    )