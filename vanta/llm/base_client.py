"""Abstract base class for all LLM clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMClient(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system: str = "", stream: bool = False) -> str:
        """Make a completion request. Return full response text."""
        ...

    async def stream_complete(self, prompt: str, system: str = "") -> AsyncGenerator[str, None]:
        """Yield response tokens. Default: buffer and yield the full result once."""
        result = await self.complete(prompt, system=system)
        yield result
