import json
from pathlib import Path
from typing import Any

import chromadb

from app.models.embedded_chunk import EmbeddedChunk


class ChromaVectorStore:
    """Persistent local vector store backed by ChromaDB."""

    def __init__(
        self,
        persist_directory: str | Path,
        collection_name: str = "nexusrag",
    ) -> None:
        if not collection_name.strip():
            raise ValueError("collection_name cannot be empty.")

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def upsert(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        """Insert or update embedded chunks."""

        if not embedded_chunks:
            return

        ids: list[str] = []
        embeddings: list[list[float]] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for item in embedded_chunks:
            chunk = item.chunk

            ids.append(chunk.id)
            embeddings.append(list(item.vector))
            documents.append(chunk.text)

            metadatas.append(
                {
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "source": chunk.source,
                    "file_type": chunk.file_type,
                    "metadata_json": json.dumps(
                        chunk.metadata,
                        sort_keys=True,
                    ),
                }
            )

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        vector: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for chunks nearest to the supplied vector."""

        if not vector:
            raise ValueError("Query vector cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if self.count() == 0:
            return []

        results = self.collection.query(
            query_embeddings=[vector],
            n_results=min(top_k, self.count()),
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        matches: list[dict[str, Any]] = []

        for chunk_id, text, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
            strict=True,
        ):
            original_metadata = json.loads(
                metadata.get("metadata_json", "{}")
            )

            matches.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": metadata["document_id"],
                    "chunk_index": metadata["chunk_index"],
                    "text": text,
                    "source": metadata["source"],
                    "file_type": metadata["file_type"],
                    "metadata": original_metadata,
                    "distance": float(distance),
                }
            )

        return matches
    
    def delete(self, chunk_ids: list[str]) -> None:
        """Delete chunks by ID."""

        if not chunk_ids:
            return

        self.collection.delete(ids=chunk_ids)

    def count(self) -> int:
        """Return number of indexed chunks."""

        return self.collection.count()

    def delete_document(self, document_id: str) -> None:
        """Delete every chunk belonging to one document."""

        if not document_id.strip():
            raise ValueError("document_id cannot be empty.")

        self.collection.delete(
            where={"document_id": document_id}
        )

    def clear(self) -> None:
        """Delete every chunk in the collection."""

        existing = self.collection.get()

        ids = existing["ids"]

        if ids:
            self.collection.delete(ids=ids)