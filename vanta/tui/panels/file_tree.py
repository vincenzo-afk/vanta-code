"""Left panel: interactive file tree widget."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.widgets import DirectoryTree, Label
from textual.containers import VerticalScroll


class FileTreePanel(VerticalScroll):
    """
    Left panel showing an interactive directory tree of the project.
    Clicking a file emits a FileSelected message to the app.
    """

    DEFAULT_CSS = """
    FileTreePanel {
        width: 20%;
        background: $surface;
        border-right: solid $primary;
        padding: 0;
    }
    FileTreePanel Label {
        background: $primary;
        color: $text;
        text-style: bold;
        width: 100%;
        padding: 0 1;
    }
    """

    def __init__(self, project_root: str = ".", **kwargs):
        super().__init__(**kwargs)
        self.project_root = project_root

    def compose(self) -> ComposeResult:
        yield Label("📁 FILES")
        root = Path(self.project_root).resolve()
        if root.exists():
            yield DirectoryTree(str(root))
        else:
            yield Label(f"[red]Path not found:\n{root}[/red]")
