"""Inline plot rendering widget (wraps plotext output in a Static)."""

from __future__ import annotations

from textual.widgets import Static
from textual.app import RenderResult


class PlotWidget(Static):
    """Displays a plotext chart string inside a scrollable Static widget."""

    DEFAULT_CSS = """
    PlotWidget {
        height: auto;
        overflow-y: auto;
        background: $background;
    }
    """

    def __init__(self, chart_str: str = "", **kwargs):
        super().__init__(chart_str, **kwargs)
        self._chart = chart_str

    def update_chart(self, chart_str: str) -> None:
        self._chart = chart_str
        self.update(chart_str)
