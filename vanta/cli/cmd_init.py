"""vanta init — initialize Vanta Code for the current project."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from vanta.config.defaults import DEFAULT_TOML

console = Console()


def init(
    path: str = typer.Option(".", help="Project root directory to initialize."),
    force: bool = typer.Option(False, "--force", help="Re-index even if .vanta/ exists."),
    no_index: bool = typer.Option(False, "--no-index", help="Create config only, skip indexing."),
    theme: str = typer.Option("classic", help="Default theme: classic | hacker | sakura."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done."),
) -> None:
    """Initialize Vanta Code for the current project."""
    from vanta.tui.themes import get_theme

    theme_data = get_theme(theme)
    console.print(f"[bold cyan]{theme_data['banner']}[/bold cyan]")
    console.print(f"[bold]Vanta Code — Initializing...[/bold]\n")

    root = Path(path).resolve()
    vanta_dir = root / ".vanta"

    if vanta_dir.exists() and not force:
        console.print("[yellow]Already initialized. Use --force to re-index.[/yellow]")
        raise typer.Exit()

    if dry_run:
        console.print(f"[dim][DRY RUN] Would create {vanta_dir}/[/dim]")
        console.print(f"[dim][DRY RUN] Would write vanta.toml with theme={theme}[/dim]")
        raise typer.Exit()

    # Create .vanta/
    vanta_dir.mkdir(parents=True, exist_ok=True)
    (vanta_dir / "logs").mkdir(exist_ok=True)
    console.print(f"  [green]✓[/green] Created {vanta_dir}/")

    # Write vanta.toml
    toml_path = root / "vanta.toml"
    toml_path.write_text(DEFAULT_TOML.format(theme=theme), encoding="utf-8")
    console.print(f"  [green]✓[/green] Generated vanta.toml")

    # Index the codebase
    if not no_index:
        console.print("  Indexing codebase...", end="")
        try:
            from vanta.memory.indexer import Indexer

            indexer = Indexer(project_root=str(root))
            stats = asyncio.run(indexer.run())
            console.print(
                f"\n  [green]✓[/green] Indexed {stats['files']} files, "
                f"{stats['chunks']} chunks, "
                f"{stats['graph_nodes']} graph nodes"
            )
        except Exception as exc:
            console.print(f"\n  [yellow]⚠ Indexing skipped: {exc}[/yellow]")

    console.print(f"\n[bold green]Done![/bold green] Run [cyan]vanta chat[/cyan] to start.")
