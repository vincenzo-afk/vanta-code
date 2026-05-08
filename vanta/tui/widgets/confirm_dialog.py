"""Modal confirmation dialog for destructive operations."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Horizontal


class ConfirmDialog(ModalScreen[bool]):
    """
    Modal confirmation dialog. Returns True if confirmed, False if cancelled.

    Usage:
        confirmed = await app.push_screen_wait(ConfirmDialog("Delete file.py?"))
    """

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }
    ConfirmDialog > * {
        background: $surface;
        border: solid $accent;
        padding: 1 2;
        width: 50;
        height: auto;
    }
    ConfirmDialog Label {
        margin-bottom: 1;
        text-align: center;
        width: 100%;
    }
    ConfirmDialog Horizontal {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    ConfirmDialog Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with self.prevent():
            yield Label(self.message)
            with Horizontal():
                yield Button("Yes", variant="error", id="yes")
                yield Button("No", variant="default", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


async def prompt_confirm(app, message: str) -> bool:
    """Push a ConfirmDialog and await its result."""
    return await app.push_screen_wait(ConfirmDialog(message))
