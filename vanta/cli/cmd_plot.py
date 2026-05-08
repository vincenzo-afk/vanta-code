"""vanta plot — read CSV/JSON and render inline terminal chart."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console

console = Console()


def plot(
    file: str = typer.Argument(..., help="CSV or JSON data file to plot."),
    chart_type: str = typer.Option("line", "--type", "-t", help="line|bar|scatter|hist"),
    title: str = typer.Option("", "--title", help="Chart title."),
    x_col: Optional[str] = typer.Option(None, "--x", help="Column name for X axis (CSV)."),
    y_col: Optional[str] = typer.Option(None, "--y", help="Column name for Y axis (CSV)."),
    width: int = typer.Option(80, "--width", help="Chart width in chars."),
    height: int = typer.Option(24, "--height", help="Chart height in rows."),
) -> None:
    """Read a data file and render an inline terminal chart."""
    from pathlib import Path

    path = Path(file)
    if not path.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    # Load data
    data: list = []
    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            import json
            raw = json.loads(path.read_text())
            if isinstance(raw, list):
                data = [float(v) for v in raw if isinstance(v, (int, float))]
        elif suffix in (".csv", ".tsv"):
            import csv
            sep = "\t" if suffix == ".tsv" else ","
            rows = list(csv.DictReader(path.open(), delimiter=sep))
            if y_col and y_col in rows[0]:
                if x_col and x_col in rows[0]:
                    data = [[float(r[x_col]), float(r[y_col])] for r in rows]
                else:
                    data = [float(r[y_col]) for r in rows]
            else:
                # Take first numeric column
                first_col = next(
                    (k for k in rows[0] if rows[0][k].replace(".", "").lstrip("-").isdigit()),
                    None
                )
                if first_col:
                    data = [float(r[first_col]) for r in rows]
        else:
            # Plain numbers, one per line
            data = [float(line.strip()) for line in path.read_text().splitlines() if line.strip()]
    except Exception as exc:
        console.print(f"[red]Failed to parse data: {exc}[/red]")
        raise typer.Exit(1)

    if not data:
        console.print("[yellow]No numeric data found in file.[/yellow]")
        raise typer.Exit(1)

    from vanta.tools.plot_tools import plot_data

    chart = asyncio.run(
        plot_data(data=data, chart_type=chart_type, title=title, width=width, height=height)
    )
    console.print(chart)
