"""Status bar widget with animated spinner and agent state display."""

from __future__ import annotations

from textual.widget import Widget
from textual.reactive import reactive
from textual.app import RenderResult
from rich.text import Text

SPINNER_STATES: dict[str, tuple[str, str, str]] = {
    "idle":       ("✓", "green",   "Ready"),
    "planning":   ("◆", "blue",    "Planning..."),
    "acting":     ("●", "yellow",  "Acting..."),
    "reflecting": ("◇", "cyan",    "Reflecting..."),
    "debugging":  ("✗", "red",     "Debugging..."),
    "indexing":   ("⊙", "magenta", "Indexing..."),
    "thinking":   ("~", "white",   "Thinking..."),
}


class StatusBar(Widget):
    """Bottom status bar showing agent state, model, and memory usage."""

    agent_state: reactive[str] = reactive("idle")
    model_name: reactive[str] = reactive("groq/llama3")
    memory_pct: reactive[int] = reactive(0)

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $panel;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def render(self) -> RenderResult:
        icon, color, label = SPINNER_STATES.get(
            self.agent_state, ("·", "white", self.agent_state)
        )
        text = Text()
        text.append(f" {icon} ", style=f"bold {color}")
        text.append(label, style=color)
        text.append(f"  ░ model: {self.model_name}", style="dim")
        if self.memory_pct > 0:
            text.append(f"  ░ mem: {self.memory_pct}%", style="dim")
        return text

    def set_state(self, state: str) -> None:
        self.agent_state = state

    def set_model(self, model: str) -> None:
        self.model_name = model
