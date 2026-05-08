"""SentenceTransformer embedding generation (local, no API cost)."""

from __future__ import annotations

from functools import lru_cache

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedder():
    """Load the SentenceTransformer model (cached — loads once per process)."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def embed(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embedding vectors (list[float]).
    """
    model = get_embedder()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()
