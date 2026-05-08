"""Root Typer app — registers all CLI subcommands."""

from __future__ import annotations

import typer

from vanta.cli.cmd_init import init
from vanta.cli.cmd_chat import chat
from vanta.cli.cmd_run import run
from vanta.cli.cmd_plot import plot
from vanta.cli.cmd_debug import debug
from vanta.cli.cmd_commit import commit
from vanta.cli.cmd_search import search
from vanta.cli.cmd_config import config_app
from vanta import __version__

app = typer.Typer(
    name="vanta",
    help="Vanta Code — The autonomous CLI coding agent with a soul.",
    add_completion=False,
    rich_markup_mode="rich",
)

app.command("init")(init)
app.command("chat")(chat)
app.command("run")(run)
app.command("plot")(plot)
app.command("debug")(debug)
app.command("commit")(commit)
app.command("search")(search)
app.add_typer(config_app, name="config")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Vanta Code v{__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
) -> None:
    """Vanta Code — The autonomous CLI coding agent with a soul."""


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
