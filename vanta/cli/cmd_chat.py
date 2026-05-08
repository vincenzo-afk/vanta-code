"""vanta chat — launch the Textual TUI."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console

console = Console()


def chat(
    theme: str = typer.Option(None, help="Override theme for this session."),
    model: str = typer.Option(None, help="Override LLM model."),
    no_memory: bool = typer.Option(False, "--no-memory", help="Disable memory retrieval."),
    plain: bool = typer.Option(False, "--plain", help="Use plain Rich output (no TUI)."),
) -> None:
    """Launch the full Textual TUI for an interactive session."""
    from vanta.config.loader import load_config

    config = load_config()

    # Prompt for API key if not set
    if not config.llm.groq_api_key:
        config.llm.groq_api_key = typer.prompt("Enter Groq API key (securely stored for session)", hide_input=True)

    if theme:
        config.tui.theme = theme
    if model:
        config.llm.groq_model = model
    if no_memory:
        config.memory.enabled = False

    if plain:
        from vanta.agent.loop import run_plain_mode
        asyncio.run(run_plain_mode(config))
        return

    try:
        from vanta.tui.app import VantaApp
        VantaApp(config=config).run()
    except ImportError as exc:
        console.print(f"[yellow]Textual not available ({exc}). Falling back to plain mode.[/yellow]")
        from vanta.agent.loop import run_plain_mode
        asyncio.run(run_plain_mode(config))
