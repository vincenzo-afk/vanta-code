"""Multi-line input bar with message history navigation."""

from __future__ import annotations

from textual.widgets import Input
from textual.app import on
from textual import events


class InputBar(Input):
    """
    Single-line input bar with up/down history navigation.
    Emits 'submitted' message when Ctrl+Enter or Enter is pressed.
    """

    DEFAULT_CSS = """
    InputBar {
        height: 3;
        border: solid $accent;
        background: $surface;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(placeholder="❯ Type your message or /command...", **kwargs)
        self._history: list[str] = []
        self._history_idx: int = -1

    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if self._history:
                self._history_idx = min(self._history_idx + 1, len(self._history) - 1)
                self.value = self._history[-(self._history_idx + 1)]
            event.stop()
        elif event.key == "down":
            if self._history_idx > 0:
                self._history_idx -= 1
                self.value = self._history[-(self._history_idx + 1)]
            elif self._history_idx == 0:
                self._history_idx = -1
                self.value = ""
            event.stop()

    def submit(self) -> str:
        """Get value, add to history, clear input."""
        value = self.value.strip()
        if value:
            self._history.append(value)
            self._history_idx = -1
        self.value = ""
        return value
