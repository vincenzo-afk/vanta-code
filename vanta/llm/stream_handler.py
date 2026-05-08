"""Unified streaming response handler for all LLM clients."""

from __future__ import annotations

from typing import AsyncGenerator, Callable


async def stream_to_callback(
    generator: AsyncGenerator[str, None],
    callback: Callable[[str], None],
) -> str:
    """
    Consume a token stream, calling callback(token) for each chunk.

    Returns the full assembled response string.
    """
    parts: list[str] = []
    async for token in generator:
        parts.append(token)
        callback(token)
    return "".join(parts)


async def collect_stream(generator: AsyncGenerator[str, None]) -> str:
    """Consume a token stream and return the full assembled response."""
    parts: list[str] = []
    async for token in generator:
        parts.append(token)
    return "".join(parts)
