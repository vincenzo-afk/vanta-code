"""Syntax-highlighted unified diff widget."""

from __future__ import annotations

from textual.widget import Widget
from textual.app import RenderResult
from rich.text import Text


class DiffViewer(Widget):
    """Renders a unified diff string with syntax highlighting."""

    DEFAULT_CSS = """
    DiffViewer {
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(self, diff_str: str, language: str = "python", **kwargs):
        super().__init__(**kwargs)
        self.diff_str = diff_str
        self.language = language

    def render(self) -> RenderResult:
        text = Text()
        for line in self.diff_str.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                text.append(line + "\n", style="bold green on dark_green")
            elif line.startswith("-") and not line.startswith("---"):
                text.append(line + "\n", style="bold red on dark_red")
            elif line.startswith("@@"):
                text.append(line + "\n", style="cyan")
            elif line.startswith("---") or line.startswith("+++"):
                text.append(line + "\n", style="dim")
            else:
                text.append(line + "\n", style="")
        return text

    def update_diff(self, diff_str: str) -> None:
        self.diff_str = diff_str
        self.refresh()
