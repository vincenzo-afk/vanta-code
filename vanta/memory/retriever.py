"""Retriever — query interface combining ChromaDB similarity + graph traversal."""

from __future__ import annotations

import fnmatch

from vanta.memory.chroma_store import ChromaStore
from vanta.memory.embedder import embed
from vanta.memory.graph import CodeGraph


class Retriever:
    """
    Unified query interface over the Memory Brain.

    Combines:
    - ChromaDB vector similarity search
    - NetworkX graph traversal for related files
    """

    def __init__(self, config=None):
        if config is None:
            raise ValueError("Retriever requires a config object")
        self.store = ChromaStore(config.memory.chroma_path)
        self.graph = CodeGraph(config.memory.graph_path)

    async def query(
        self, text: str, top_k: int = 5, file_filter: str | None = None
    ) -> list[dict]:
        """
        Semantic search over the indexed codebase.

        Args:
            text: Natural language or code query.
            top_k: Number of results to return.
            file_filter: Glob pattern to restrict results (e.g. '*.py').

        Returns:
            List of result dicts with content, file, start_line, end_line, score, related_files.
        """
        if self.store.count() == 0:
            return []

        emb = embed([text])[0]

        # Build ChromaDB where filter
        where: dict | None = None
        if file_filter:
            # ChromaDB supports $contains for substring matching
            needle = file_filter.replace("*", "").replace("?", "")
            if needle:
                where = {"file": {"$contains": needle}}

        results = self.store.query(emb, top_k=top_k, where=where)

        # Post-filter by glob if chromadb where wasn't sufficient
        if file_filter:
            results = [
                r for r in results
                if r.get("file") and fnmatch.fnmatch(r["file"], f"*{file_filter.strip('*')}")
            ]

        # Augment with graph neighbors
        for r in results:
            if r.get("file"):
                r["related_files"] = self.graph.get_related(r["file"], depth=1)
            else:
                r["related_files"] = []

        return results
