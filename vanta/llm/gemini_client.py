"""Async Gemini API client."""

from __future__ import annotations

import os

import httpx

from vanta.llm.base_client import BaseLLMClient


class GeminiClient(BaseLLMClient):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, config=None):
        self.config = config
        self.model = (
            config.llm.gemini_model
            if config
            else os.getenv("VANTA_GEMINI_MODEL", "gemini-1.5-flash")
        )
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set in environment / .env")

    async def complete(self, prompt: str, system: str = "", stream: bool = False) -> str:
        """Send a completion request to Gemini and return the response text."""
        url = self.BASE_URL.format(model=self.model) + f"?key={self.api_key}"

        max_tokens = self.config.llm.max_tokens if self.config else 4096
        temperature = self.config.llm.temperature if self.config else 0.2

        payload: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
