"""Plot tool: render inline ASCII/Unicode charts with plotext."""

from __future__ import annotations

import io
import sys

from vanta.tools.registry import tool


@tool("plot_data", "Render an inline terminal chart with plotext.")
async def plot_data(
    data: list,
    chart_type: str = "line",
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    width: int = 80,
    height: int = 24,
    config=None,
    state=None,
) -> str:
    """
    Render an inline ASCII/Unicode chart in the terminal using plotext.

    Args:
        data: Y values (list[float]) or [X, Y] pairs (list[list[float]]).
        chart_type: 'line', 'bar', 'scatter', or 'hist'.
        title: Chart title.
        x_label: X-axis label.
        y_label: Y-axis label.
        width: Terminal width in chars (default 80).
        height: Terminal height in rows (default 24).

    Returns:
        Rendered chart as string (for embedding in TUI widget).
    """
    try:
        import plotext as plt
    except ImportError:
        return "[plotext not installed — run: pip install plotext]"

    plt.clf()
    plt.plotsize(width, height)
    if title:
        plt.title(title)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)

    if chart_type == "line":
        plt.plot(data)
    elif chart_type == "bar":
        plt.bar(data)
    elif chart_type == "scatter":
        if data and isinstance(data[0], (list, tuple)):
            plt.scatter([d[0] for d in data], [d[1] for d in data])
        else:
            plt.scatter(data)
    elif chart_type == "hist":
        plt.hist(data)
    else:
        raise ValueError(f"Unknown chart_type: {chart_type}. Use line, bar, scatter, or hist.")

    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        plt.show()
    finally:
        sys.stdout = old_stdout
    return buf.getvalue()
