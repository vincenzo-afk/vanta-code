"""Reflector — post-action self-evaluation and task completion check."""

from __future__ import annotations

import json
import re

from vanta.agent.prompt_builder import build_reflector_prompt
from vanta.llm.router import route_query
from vanta.models import SessionState, ToolResult


class Reflector:
    """
    After executing a plan, the Reflector evaluates whether the task
    is complete, or generates a new sub-plan for remaining work.
    """

    def __init__(self, config=None):
        self.config = config

    async def reflect(
        self, task: str, results: list[ToolResult], state: SessionState
    ) -> dict:
        """
        Evaluate results and determine next action.

        Returns:
            {
                "complete": bool,
                "next_steps": list[dict],   # empty if complete
                "summary": str,
            }
        """
        results_summary = self._summarize_results(results)
        prompt = build_reflector_prompt(task, results_summary)

        response = await route_query(task=prompt, complexity="low", config=self.config)
        return self._parse_reflection(response, results)

    def _summarize_results(self, results: list[ToolResult]) -> str:
        lines: list[str] = []
        for i, r in enumerate(results, 1):
            status = "✓" if r.success else "✗"
            output_preview = (r.output or "")[:200]
            error_info = f" | Error: {r.error}" if r.error else ""
            lines.append(f"{i}. {status} {output_preview}{error_info}")
        return "\n".join(lines) if lines else "No results yet."

    def _parse_reflection(self, response: str, results: list[ToolResult]) -> dict:
        """Parse JSON reflection response from LLM."""
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return {
                    "complete": bool(data.get("complete", False)),
                    "next_steps": data.get("next_steps", []),
                    "summary": data.get("summary", response[:300]),
                }
            except (json.JSONDecodeError, KeyError):
                pass

        # Heuristic fallback: check if all results succeeded
        all_success = all(r.success for r in results)
        return {
            "complete": all_success,
            "next_steps": [],
            "summary": response[:300],
        }
