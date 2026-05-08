"""ChromaDB client wrapper for persistent vector storage."""

from __future__ import annotations

from pathlib import Path


class ChromaStore:
    """
    Thin wrapper around a ChromaDB persistent collection.
    Stores code chunks as embeddings with file/line metadata.
    """

    def __init__(self, persist_dir: str):
        import chromadb

        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="vanta_codebase",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update chunks in the collection."""
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        """
        Query the collection by embedding similarity.

        Returns:
            List of dicts with content, file, start_line, end_line, score.
        """
        kwargs: dict = {
            "query_embeddings": [embedding],
            "n_results": min(top_k, self.collection.count() or 1),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)
        output: list[dict] = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            output.append(
                {
                    "content": doc,
                    "file": meta.get("file"),
                    "start_line": meta.get("start_line"),
                    "end_line": meta.get("end_line"),
                    "language": meta.get("language", ""),
                    "score": 1 - distance,  # cosine similarity
                }
            )
        return output

    def count(self) -> int:
        """Return total number of chunks stored."""
        return self.collection.count()

    def delete_by_file(self, file_path: str) -> None:
        """Remove all chunks belonging to a file (for re-indexing)."""
        self.collection.delete(where={"file": file_path})
