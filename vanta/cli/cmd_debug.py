"""vanta debug — manually trigger the AutoDebug loop."""

from __future__ import annotations

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax

console = Console()


def debug(
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Read traceback from file."),
    max_attempts: int = typer.Option(3, "--max-attempts", help="Max fix attempts."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show fix without applying."),
) -> None:
    """Read a traceback from stdin or file and run the AutoDebug loop."""
    from vanta.config.loader import load_config

    config = load_config()
    if dry_run:
        config.dry_run = True

    # Read traceback
    if file:
        from pathlib import Path
        p = Path(file)
        if not p.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise typer.Exit(1)
        traceback = p.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            console.print("[yellow]Paste the traceback (Ctrl+D when done):[/yellow]")
        traceback = sys.stdin.read()

    if not traceback.strip():
        console.print("[yellow]No traceback provided.[/yellow]")
        raise typer.Exit(1)

    console.print(Syntax(traceback, "python-traceback", theme="monokai"))
    console.rule("[bold cyan]AutoDebug[/bold cyan]")

    from vanta.tools.debug_tools import auto_debug
    from vanta.models import SessionState

    state = SessionState()
    result = asyncio.run(
        auto_debug(traceback=traceback, max_attempts=max_attempts, config=config, state=state)
    )

    if result["fixed"]:
        console.print(
            f"[green]✓ Fixed in {result['attempts']} attempt(s).[/green]\n"
            f"Patch applied:\n{result.get('patch_applied', '')[:500]}"
        )
    else:
        console.print(
            f"[red]✗ {result['message']}[/red]\n"
            "Manual intervention required."
        )
        raise typer.Exit(1)
