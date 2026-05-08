"""Async spinner context manager for Rich console output."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

_console = Console()


@asynccontextmanager
async def spin(message: str, spinner_name: str = "dots") -> AsyncGenerator[None, None]:
    """
    Async context manager that shows a Rich spinner while work executes.

    Usage:
        async with spin("Indexing codebase..."):
            await do_heavy_work()
    """
    spinner = Spinner(spinner_name, text=message, style="bold cyan")
    with Live(spinner, console=_console, refresh_per_second=12, transient=True):
        yield
