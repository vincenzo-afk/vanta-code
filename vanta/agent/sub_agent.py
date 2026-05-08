"""Sub-agent — spawns async sub-agents for parallel task execution."""

from __future__ import annotations

import asyncio

from vanta.agent.executor import Executor
from vanta.models import PlanStep, SessionState, ToolResult


class SubAgent:
    """
    A lightweight async sub-agent that executes a single step in isolation.
    Shares the parent SessionState behind an asyncio.Lock for thread safety.
    """

    def __init__(self, executor: Executor, state: SessionState, lock: asyncio.Lock):
        self.executor = executor
        self.state = state
        self.lock = lock

    async def run_step(self, step: PlanStep) -> ToolResult:
        """Execute a single step in isolation. Thread-safe via lock."""
        result = await self.executor._run_step(step, self.state)
        async with self.lock:
            self.state.results.append(result)
        return result


async def run_parallel_steps(
    steps: list[PlanStep],
    executor: Executor,
    state: SessionState,
) -> list[ToolResult]:
    """Run a list of steps concurrently using sub-agents."""
    lock = asyncio.Lock()
    agents = [SubAgent(executor, state, lock) for _ in steps]
    tasks = [agent.run_step(step) for agent, step in zip(agents, steps)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    tool_results: list[ToolResult] = []
    for step, result in zip(steps, results):
        if isinstance(result, Exception):
            tool_results.append(
                ToolResult(success=False, output="", error=str(result))
            )
        else:
            tool_results.append(result)
    return tool_results
