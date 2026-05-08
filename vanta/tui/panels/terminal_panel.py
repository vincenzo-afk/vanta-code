"""Right panel: shell output, spinners, logs."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, RichLog


class TerminalPanel(VerticalScroll):
    """Right panel showing shell output, tool results, and logs."""

    DEFAULT_CSS = """
    TerminalPanel {
        width: 25%;
        background: $surface;
        border-left: solid $primary;
        padding: 0;
    }
    TerminalPanel Label {
        background: $primary;
        color: $text;
        text-style: bold;
        width: 100%;
        padding: 0 1;
    }
    TerminalPanel RichLog {
        height: 1fr;
        background: $surface;
        padding: 0 1;
        scrollbar-size: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("⚡ TERMINAL")
        yield RichLog(id="terminal-log", highlight=True, markup=True)

    def write(self, text: str, style: str = "") -> None:
        """Append a line to the terminal log."""
        log = self.query_one("#terminal-log", RichLog)
        if style:
            log.write(f"[{style}]{text}[/{style}]")
        else:
            log.write(text)

    def write_success(self, text: str) -> None:
        self.write(f"✓ {text}", style="green")

    def write_error(self, text: str) -> None:
        self.write(f"✗ {text}", style="red")

    def write_info(self, text: str) -> None:
        self.write(f"ℹ {text}", style="cyan")

    def clear(self) -> None:
        self.query_one("#terminal-log", RichLog).clear()
