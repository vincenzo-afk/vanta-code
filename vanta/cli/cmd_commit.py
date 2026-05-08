"""vanta commit — AI-generated git commit message + optional push."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console

console = Console()


def commit(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Override AI message."),
    files: Optional[str] = typer.Option(None, "--files", help="Comma-separated files to stage."),
    push: bool = typer.Option(False, "--push", help="Push to remote after commit."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show message without committing."),
) -> None:
    """Stage all changes, generate an AI commit message, and create a git commit."""
    from vanta.config.loader import load_config
    from vanta.tools.git_tools import git_commit
    from vanta.models import SessionState

    config = load_config()
    if dry_run:
        config.dry_run = True

    file_list = [f.strip() for f in files.split(",")] if files else None
    state = SessionState()

    with console.status("[cyan]Generating commit...[/cyan]"):
        result = asyncio.run(
            git_commit(message=message, files=file_list, config=config, state=state)
        )

    console.print(f"[green]✓[/green] {result}")

    if push and not dry_run:
        import subprocess
        proc = subprocess.run(["git", "push"], capture_output=True, text=True)
        if proc.returncode == 0:
            console.print("[green]✓[/green] Pushed to remote.")
        else:
            console.print(f"[red]Push failed:[/red] {proc.stderr}")
            raise typer.Exit(1)
