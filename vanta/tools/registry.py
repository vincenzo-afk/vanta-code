"""Tool registry: @tool decorator + dispatch function."""

from __future__ import annotations

import inspect
from typing import Any, Callable

from vanta.models import ToolCall, ToolResult

TOOL_REGISTRY: dict[str, dict[str, Any]] = {}


def tool(name: str, description: str) -> Callable:
    """Decorator that registers a function as an agent-callable tool."""

    def decorator(fn: Callable) -> Callable:
        TOOL_REGISTRY[name] = {
            "fn": fn,
            "description": description,
            "schema": _build_schema(fn),
        }
        return fn

    return decorator


def _python_type_to_json(annotation: Any) -> str:
    """Convert a Python type annotation to a JSON schema type string."""
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        return "array"
    if annotation in (int,):
        return "integer"
    if annotation in (float,):
        return "number"
    if annotation in (bool,):
        return "boolean"
    return "string"


def _build_schema(fn: Callable) -> dict[str, Any]:
    """Auto-generate a JSON schema dict from the function's type hints."""
    sig = inspect.signature(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("config", "state", "self"):
            continue
        annotation = param.annotation
        prop: dict[str, Any] = {"type": _python_type_to_json(annotation)}
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        properties[param_name] = prop

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


async def dispatch(call: ToolCall, config: Any = None, state: Any = None) -> ToolResult:
    """Look up and call the registered tool. Returns a ToolResult."""
    import time

    entry = TOOL_REGISTRY.get(call.tool)
    if not entry:
        return ToolResult(
            success=False,
            output="",
            error=f"Unknown tool: {call.tool}",
            tool_call_id=call.id,
        )
    start = time.monotonic()
    try:
        result = await entry["fn"](**call.params, config=config, state=state)
        duration = (time.monotonic() - start) * 1000
        return ToolResult(
            success=True,
            output=str(result),
            error=None,
            duration_ms=duration,
            tool_call_id=call.id,
        )
    except Exception as exc:
        duration = (time.monotonic() - start) * 1000
        return ToolResult(
            success=False,
            output="",
            error=str(exc),
            duration_ms=duration,
            tool_call_id=call.id,
        )


def get_tool_schemas() -> list[dict[str, Any]]:
    """Return all registered tool schemas (for LLM function-calling)."""
    return [
        {
            "name": name,
            "description": entry["description"],
            "parameters": entry["schema"],
        }
        for name, entry in TOOL_REGISTRY.items()
    ]
