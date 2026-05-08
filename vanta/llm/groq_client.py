"""Async Groq API client with streaming support."""

from __future__ import annotations

import json
import os
from collections.abc import AsyncGenerator

import httpx

from vanta.llm.base_client import BaseLLMClient


class GroqClient(BaseLLMClient):
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, config=None):
        self.config = config
        self.model = (
            config.llm.groq_model if config else os.getenv("VANTA_GROQ_MODEL", "llama3-70b-8192")
        )
        self.api_key = (
            config.llm.groq_api_key if config and config.llm.groq_api_key
            else os.getenv("GROQ_API_KEY", "")
        )
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set in environment / config")
        if self.api_key == "your_groq_api_key_here" or not self.api_key.startswith("gsk_"):
            raise ValueError(f"Invalid GROQ_API_KEY format: must start with 'gsk_' and not be placeholder. Current key starts with: {self.api_key[:4]}...")

    async def complete(self, prompt: str, system: str = "", stream: bool = False) -> str:
        """Send a completion request to Groq and return the response text."""
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        max_tokens = self.config.llm.max_tokens if self.config else 4096
        temperature = self.config.llm.temperature if self.config else 0.2

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def stream_complete(self, prompt: str, system: str = "") -> AsyncGenerator[str, None]:  # type: ignore[override]
        """Yield tokens as they stream from Groq."""
        messages: list[dict] = []
        if system:
            messages.insert(0, {"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120) as client, client.stream(
            "POST",
            self.BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": messages, "stream": True},
        ) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
