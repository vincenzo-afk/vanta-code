"""Search tools: search_codebase, web_search_docs."""

from __future__ import annotations

import httpx

from vanta.tools.registry import tool

SEARXNG_INSTANCE = "https://searx.be"


@tool("search_codebase", "Semantic search over the indexed codebase.")
async def search_codebase(
    query: str,
    top_k: int = 5,
    file_filter: str | None = None,
    config=None,
    state=None,
) -> list:
    """
    Semantic search over the indexed codebase using ChromaDB.

    Args:
        query: Natural language or code query.
        top_k: Number of results to return (default 5).
        file_filter: Glob pattern to restrict search (e.g. '*.py').

    Returns:
        list[dict] — Each dict has file, start_line, end_line, content, score.
    """
    if not config or not config.memory.enabled:
        return [{"content": "Memory not enabled.", "file": None, "score": 0}]

    from vanta.memory.retriever import Retriever

    retriever = Retriever(config=config)
    results = await retriever.query(query, top_k=top_k, file_filter=file_filter)
    return results


@tool("web_search_docs", "Search documentation and summarize results.")
async def web_search_docs(
    query: str,
    max_results: int = 3,
    config=None,
    state=None,
) -> str:
    """
    Search for documentation, API references, and answers using SearXNG.
    Summarizes the top results into a concise answer via LLM.

    Args:
        query: Documentation search query.
        max_results: Number of results to fetch (default 3).

    Returns:
        Summarized documentation answer.
    """
    searxng_url = SEARXNG_INSTANCE
    if config:
        # Allow override via env / config
        import os
        searxng_url = os.getenv("VANTA_SEARXNG_URL", SEARXNG_INSTANCE)

    snippets = ""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{searxng_url}/search",
                params={"q": query, "format": "json", "categories": "general"},
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])[:max_results]
        snippets = "\n\n".join(
            f"**{r['title']}** ({r.get('url', '')})\n{r.get('content', '')}"
            for r in results
        )
    except Exception as exc:
        return f"Web search failed: {exc}"

    if not snippets:
        return "No results found."

    from vanta.llm.router import route_query

    summary = await route_query(
        task=f"Summarize these search results for the query '{query}':\n{snippets}",
        complexity="low",
        config=config,
    )
    return summary
