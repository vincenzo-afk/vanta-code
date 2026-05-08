"""vanta config — view and edit vanta.toml settings."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.pretty import pprint

console = Console()
config_app = typer.Typer(help="View and edit vanta.toml settings.")


@config_app.command("show")
def show() -> None:
    """Pretty-print the current config."""
    from vanta.config.loader import load_config
    config = load_config()
    pprint(config.model_dump(), console=console)


@config_app.command("set")
def set_value(
    key: str = typer.Argument(..., help="Dot-notation key, e.g. tui.theme"),
    value: str = typer.Argument(..., help="New value to set."),
) -> None:
    """Set a config value in vanta.toml (e.g. vanta config set tui.theme hacker)."""
    from pathlib import Path
    import re

    toml_path = _find_toml()
    if not toml_path:
        console.print("[red]No vanta.toml found. Run 'vanta init' first.[/red]")
        raise typer.Exit(1)

    content = toml_path.read_text(encoding="utf-8")
    # Map dot-notation key to TOML section.key
    parts = key.split(".", 1)
    if len(parts) == 2:
        section, k = parts
        pattern = rf'(?<={re.escape(k)}\s*=\s*)[^\n]+'
        replacement = _format_toml_value(value)
        new_content = re.sub(pattern, replacement, content, count=1)
    else:
        pattern = rf'(?<={re.escape(key)}\s*=\s*)[^\n]+'
        new_content = re.sub(pattern, _format_toml_value(value), content, count=1)

    if new_content == content:
        console.print(f"[yellow]Key '{key}' not found in vanta.toml.[/yellow]")
    else:
        toml_path.write_text(new_content, encoding="utf-8")
        console.print(f"[green]✓[/green] Set {key} = {value}")


@config_app.command("reset")
def reset() -> None:
    """Reset vanta.toml to default values."""
    from vanta.config.defaults import DEFAULT_TOML

    toml_path = _find_toml()
    if not toml_path:
        console.print("[red]No vanta.toml found.[/red]")
        raise typer.Exit(1)

    confirm = typer.confirm("Reset vanta.toml to defaults?")
    if confirm:
        toml_path.write_text(DEFAULT_TOML.format(theme="classic"), encoding="utf-8")
        console.print("[green]✓[/green] vanta.toml reset to defaults.")


def _find_toml():
    from pathlib import Path
    current = Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / "vanta.toml"
        if candidate.exists():
            return candidate
    return None


def _format_toml_value(value: str) -> str:
    """Format a string value for TOML (add quotes if needed)."""
    try:
        float(value)
        return value
    except ValueError:
        pass
    if value.lower() in ("true", "false"):
        return value.lower()
    return f'"{value}"'
