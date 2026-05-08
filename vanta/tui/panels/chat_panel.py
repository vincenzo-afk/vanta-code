"""Center panel: chat history + diff renderer."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, Markdown, Static
from rich.text import Text

from vanta.tui.widgets.diff_viewer import DiffViewer


class ChatMessage(Static):
    """A single chat message bubble (user or agent)."""

    DEFAULT_CSS = """
    ChatMessage {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }
    ChatMessage.user {
        border: solid $accent;
        background: $surface;
    }
    ChatMessage.agent {
        border-left: thick $primary;
        background: $background;
    }
    """

    def __init__(self, role: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.content_text = content
        self.add_class(role)

    def compose(self) -> ComposeResult:
        label = "You" if self.role == "user" else "Vanta"
        yield Label(f"[bold]{label}[/bold]", markup=True)
        # Detect diff blocks
        if self.content_text.startswith("---") or "+++ b/" in self.content_text:
            yield DiffViewer(self.content_text)
        else:
            yield Markdown(self.content_text)


class ChatPanel(VerticalScroll):
    """Center panel: scrollable chat history."""

    DEFAULT_CSS = """
    ChatPanel {
        width: 55%;
        background: $background;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("[bold cyan]Vanta Code[/bold cyan] — start typing below.", markup=True)

    def add_message(self, role: str, content: str) -> None:
        """Append a new chat message and scroll to bottom."""
        msg = ChatMessage(role=role, content=content)
        self.mount(msg)
        self.scroll_end(animate=False)

    def clear(self) -> None:
        """Remove all messages."""
        for child in list(self.children):
            if isinstance(child, ChatMessage):
                child.remove()
