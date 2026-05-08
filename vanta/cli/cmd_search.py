"""vanta search — search documentation and summarize results."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console

console = Console()


def search(
    query: str = typer.Argument(..., help="Documentation search query."),
    site: str = typer.Option("all", "--site", help="Restrict to: pypi|so|docs|all"),
    max_results: int = typer.Option(3, "--max-results", "-n", help="Number of results."),
) -> None:
    """Search documentation and Stack Overflow, summarize results inline."""
    from vanta.config.loader import load_config
    from vanta.tools.search_tools import web_search_docs
    from vanta.models import SessionState

    config = load_config()
    state = SessionState()

    site_map = {
        "pypi": f"{query} site:pypi.org",
        "so": f"{query} site:stackoverflow.com",
        "docs": f"{query} documentation",
        "all": query,
    }
    full_query = site_map.get(site, query)

    with console.status(f"[cyan]Searching: {full_query!r}[/cyan]"):
        result = asyncio.run(
            web_search_docs(query=full_query, max_results=max_results, config=config, state=state)
        )

    console.rule(f"[bold]Results for: {query}[/bold]")
    console.print(result)
