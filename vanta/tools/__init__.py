"""Tools package — imports all tools to trigger @tool registration."""

# Importing each module causes the @tool decorators to run,
# which populates TOOL_REGISTRY automatically.
from vanta.tools import (  # noqa: F401
    file_tools,
    shell_tools,
    nav_tools,
    git_tools,
    plot_tools,
    search_tools,
    debug_tools,
)
from vanta.tools.registry import TOOL_REGISTRY, dispatch, get_tool_schemas, tool  # noqa: F401

__all__ = ["TOOL_REGISTRY", "dispatch", "get_tool_schemas", "tool"]
