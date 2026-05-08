"""Task planner — decomposes natural language tasks into atomic steps."""

from __future__ import annotations

import json
import re

from vanta.agent.prompt_builder import build_planner_prompt
from vanta.llm.router import route_query
from vanta.models import PlanStep


class Planner:
    """Calls the LLM to decompose a task into a list of PlanSteps."""

    def __init__(self, config=None):
        self.config = config

    async def plan(self, task: str) -> list[PlanStep]:
        """
        Decompose `task` into an ordered list of PlanStep objects.

        Returns a list of PlanStep objects. Falls back to a single
        'run_shell' step if parsing fails.
        """
        prompt = build_planner_prompt(task, self.config)
        response = await route_query(task=prompt, complexity="medium", config=self.config)

        steps = self._parse_steps(response)
        if not steps:
            # Fallback: single step
            steps = [
                PlanStep(
                    description=task,
                    tool="run_shell",
                    params={"command": "echo 'No plan generated'"},
                )
            ]
        return steps

    def _parse_steps(self, response: str) -> list[PlanStep]:
        """Extract JSON step list from LLM response."""
        # Try to find JSON array in the response
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            return []
        try:
            raw_steps = json.loads(match.group(0))
            steps: list[PlanStep] = []
            for raw in raw_steps:
                if not isinstance(raw, dict):
                    continue
                steps.append(
                    PlanStep(
                        description=raw.get("description", ""),
                        tool=raw.get("tool", "run_shell"),
                        params=raw.get("params", {}),
                        depends_on=raw.get("depends_on", []),
                        estimated_complexity=raw.get("estimated_complexity", "medium"),
                        can_parallelize=raw.get("can_parallelize", False),
                    )
                )
            return steps
        except (json.JSONDecodeError, KeyError, TypeError):
            return []
