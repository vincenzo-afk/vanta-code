"""vanta run — one-shot non-interactive task execution."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console

console = Console()


def run(
    task: str = typer.Argument(..., help='Task to execute, e.g. "Add type hints to utils.py"'),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without file writes."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print all tool calls."),
    no_memory: bool = typer.Option(False, "--no-memory", help="Skip memory retrieval."),
    output_file: str | None = typer.Option(None, "--output-file", help="Save output to file."),
) -> None:
    """Execute a task non-interactively and exit."""
    from vanta.agent.loop import AgentLoop
    from vanta.config.loader import load_config
    from vanta.models import SessionState

    config = load_config()

    # Prompt for API key if not set
    if not config.llm.groq_api_key:
        config.llm.groq_api_key = typer.prompt("Enter Groq API key (securely stored for session)", hide_input=True)

    if dry_run:
        config.dry_run = True
        config.agent.dry_run = True
    if no_memory:
        config.memory.enabled = False
    if verbose:
        config.agent.verbose_tools = True

    console.rule("[bold cyan]Vanta Code — Running task[/bold cyan]")
    console.print(f"[dim]Task:[/dim] {task}\n")

    state = SessionState()
    loop = AgentLoop(config=config, state=state)

    try:
        result = asyncio.run(loop.run_task(task))
        console.print(f"\n[green]{result}[/green]")

        if output_file:
            from pathlib import Path
            Path(output_file).write_text(result, encoding="utf-8")
            console.print(f"[dim]Output saved to {output_file}[/dim]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise typer.Exit(1)
